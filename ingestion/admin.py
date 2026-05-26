from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import DataSource, RawDataPayload, NormalizedEmissionRecord

@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type')

@admin.register(RawDataPayload)
class RawDataPayloadAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'status', 'ingested_at')
    list_filter = ('status', 'source')

@admin.register(NormalizedEmissionRecord)
class NormalizedEmissionRecordAdmin(SimpleHistoryAdmin):
    list_display = ('emission_source', 'scope_category', 'normalized_value', 'normalized_unit')
    list_filter = ('scope_category', 'emission_source')
    history_list_display = ["status"]