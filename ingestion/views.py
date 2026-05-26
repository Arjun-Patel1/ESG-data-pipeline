import csv
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import process_sap_payload
from .serializers import NormalizedEmissionRecordSerializer # Add to your imports
from .models import RawDataPayload, DataSource, NormalizedEmissionRecord
class ReviewQueueView(APIView):
    """Fetches normalized records that need analyst review."""
    def get(self, request):
        # Only fetch records that are flagged for review
        records = NormalizedEmissionRecord.objects.filter(raw_payload__status='NEEDS_REVIEW')
        serializer = NormalizedEmissionRecordSerializer(records, many=True)
        return Response(serializer.data)

class DataIngestionView(APIView):
    """API Endpoint to upload SAP, Utility, or Concur files directly to the Vault."""
    
    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        source_name = request.data.get('source_name', 'Unknown Source')
        source_type = request.data.get('source_type', 'UPLOAD')

        if not file_obj:
            return Response({"error": "No file uploaded. Please attach a file."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Create or find the source tracker (e.g., "SAP Export")
        source, _ = DataSource.objects.get_or_create(name=source_name, defaults={'source_type': source_type})

        try:
            # 2a. Handle CSV Files (SAP & PG&E Utility Data)
            if file_obj.name.endswith('.csv'):
                decoded_file = file_obj.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                
                payloads = []
                for row in reader:
                    payloads.append(RawDataPayload(
                        source=source,
                        raw_data=row, # Saves the raw messy row exactly as-is into JSONB
                        status='PENDING'
                    ))
                
                # Bulk create is highly efficient for large enterprise files
                RawDataPayload.objects.bulk_create(payloads)

                # --- NEW: Trigger the background normalization worker ---
                pending_payloads = RawDataPayload.objects.filter(source=source, status='PENDING')
                for p in pending_payloads:
                    process_sap_payload.delay(p.id) # The .delay() makes it asynchronous!
                # --------------------------------------------------------

                return Response(
                    {"message": f"Success: {len(payloads)} CSV rows ingested. Background normalization started."}, 
                    status=status.HTTP_202_ACCEPTED
                )

            # 2b. Handle JSON Files (Concur Travel Webhook)
            elif file_obj.name.endswith('.json'):
                data = json.load(file_obj)
                
                RawDataPayload.objects.create(
                    source=source,
                    raw_data=data,
                    status='PENDING'
                )
                return Response(
                    {"message": "Success: JSON webhook payload vaulted."}, 
                    status=status.HTTP_202_ACCEPTED
                )
            
            else:
                return Response({"error": "Unsupported file format. Use .csv or .json"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ApproveRecordView(APIView):
    """Locks the record into the immutable ledger for audit."""
    def patch(self, request, pk):
        try:
            record = NormalizedEmissionRecord.objects.get(id=pk)
            # Find the original vault payload and lock it
            record.raw_payload.status = 'APPROVED'
            record.raw_payload.save()
            return Response({"status": "Approved and locked for audit"}, status=status.HTTP_200_OK)
        except NormalizedEmissionRecord.DoesNotExist:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)