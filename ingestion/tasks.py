from celery import shared_task
from datetime import datetime
from django.conf import settings
import google.generativeai as genai
from .models import RawDataPayload, NormalizedEmissionRecord

# Configure the Google Gemini AI once when the worker starts
genai.configure(api_key=settings.GEMINI_API_KEY)
# We use 'flash' because it is extremely fast and reliable for background data processing

model = genai.GenerativeModel('gemini-2.5-flash')

@shared_task
def process_sap_payload(payload_id):
    """Background task to clean German SAP data, normalize units, and run an AI Audit."""
    try:
        payload = RawDataPayload.objects.get(id=payload_id)
        raw = payload.raw_data

        # 1. Deterministic Math (The "Blind" Cleaning)
        raw_amount = raw.get('Menge', '0')
        clean_amount = float(raw_amount.replace('.', '').replace(',', '.'))
        
        raw_unit = raw.get('Einheit', 'L')
        if raw_unit == 'GAL':
            clean_amount = clean_amount * 3.78541 # US Gallon to Liters
            clean_unit = 'Liters'
        else:
            clean_unit = 'Liters'
            
        clean_date = datetime.strptime(raw.get('Erfassungsdatum'), '%d.%m.%Y').strftime('%Y-%m-%d')
        emission_source = f"Stationary Combustion - {raw.get('Werk')} ({raw.get('Materialnummer')})"

        # 2. The AI Auditor (The Brains)
        ai_note = None
        
        # Flag anything over 2000 Liters as potentially anomalous to trigger the AI
        if clean_amount > 2000:
            prompt = f"""
            You are an expert ESG Auditor. An automated system just ingested the following data:
            Source: {emission_source}
            Amount: {clean_amount} {clean_unit}
            
            This amount is unusually high for a single daily entry. Write a strict, 1-sentence warning 
            for the human analyst reviewing this record, explaining why such a high volume of 
            combustion fuel in a single day might require a manual audit.
            """
            response = model.generate_content(prompt)
            ai_note = response.text.strip()

        # 3. Create the Versioned Ledger entry with the AI Note
        NormalizedEmissionRecord.objects.create(
            raw_payload=payload,
            scope_category='SCOPE_1',
            emission_source=emission_source,
            activity_date_start=clean_date,
            normalized_value=clean_amount,
            normalized_unit=clean_unit,
            ai_audit_note=ai_note # <--- Saves the AI's thoughts to the database!
        )

        # 4. Update Vault status so it appears in the Analyst Inbox
        payload.status = 'NEEDS_REVIEW'
        payload.save()

        return f"Successfully normalized payload {payload_id}"

    except Exception as e:
        # If it fails, log the error but keep the raw data safe!
        print(f"Error normalizing {payload_id}: {str(e)}")