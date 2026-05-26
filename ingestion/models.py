from django.db import models
from django.db.models import JSONField
from simple_history.models import HistoricalRecords

class DataSource(models.Model):
    """Tracks where the data came from (e.g., SAP, Utility Portal, Concur)."""
    name = models.CharField(max_length=255) 
    source_type = models.CharField(max_length=50) 
    
    def __str__(self):
        return self.name

class RawDataPayload(models.Model):
    """THE VAULT: Stores the exact, messy payload received from the client."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending Normalization'),
        ('NEEDS_REVIEW', 'Needs Analyst Review'),
        ('APPROVED', 'Approved for Audit'),
    ]
    
    source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    raw_data = JSONField() # This is the crucial JSONB immutable ledger
    ingested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    def __str__(self):
        return f"Raw Payload {self.id} - {self.status}"

class NormalizedEmissionRecord(models.Model):
    """THE LEDGER: The cleaned, standardized row the analyst interacts with."""
    SCOPE_CHOICES = [
        ('SCOPE_1', 'Scope 1 (Direct)'),
        ('SCOPE_2', 'Scope 2 (Indirect Electricity)'),
        ('SCOPE_3', 'Scope 3 (Value Chain)'),
    ]
    
    # Strict link back to the exact source row for the auditor
    raw_payload = models.OneToOneField(RawDataPayload, on_delete=models.CASCADE, related_name='normalized_record')
    
    scope_category = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='SCOPE_1')
    emission_source = models.CharField(max_length=100) # e.g., "Stationary Combustion", "Business Travel"
    
    activity_date_start = models.DateField()
    activity_date_end = models.DateField(null=True, blank=True)
    
    normalized_value = models.FloatField()
    normalized_unit = models.CharField(max_length=20) # MUST be standardized (e.g., 'kWh', 'Liters')
    
    # The Gemini API will automatically populate this if an anomaly is found
    ai_audit_note = models.TextField(blank=True, null=True) 
    
    # MAGIC: Automatically tracks every change an analyst makes for the audit trail
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.emission_source}: {self.normalized_value} {self.normalized_unit}"