from rest_framework import serializers
from .models import RawDataPayload, DataSource, NormalizedEmissionRecord
from .models import NormalizedEmissionRecord

class NormalizedEmissionRecordSerializer(serializers.ModelSerializer):
    raw_payload_data = serializers.JSONField(source='raw_payload.raw_data', read_only=True)
    status = serializers.CharField(source='raw_payload.status', read_only=True)
    
    class Meta:
        model = NormalizedEmissionRecord
        fields = '__all__'
class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = '__all__'

class RawDataPayloadSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    
    class Meta:
        model = RawDataPayload
        fields = ['id', 'source_name', 'raw_data', 'status', 'ingested_at']