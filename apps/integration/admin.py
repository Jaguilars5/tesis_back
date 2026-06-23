from django.contrib import admin
from .models import SyncQueue


@admin.register(SyncQueue)
class SyncQueueAdmin(admin.ModelAdmin):
    list_display = ["uuid", "source_table", "operation", "status", "created_at"]
    list_filter = ["status", "operation", "source_table"]
    search_fields = ["source_table", "record_uuid"]

