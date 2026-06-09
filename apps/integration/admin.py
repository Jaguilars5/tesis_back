from django.contrib import admin
from .models import SyncOperation, SyncQueue, SyncStatus


@admin.register(SyncQueue)
class SyncQueueAdmin(admin.ModelAdmin):
    list_display = ["uuid", "source_table", "operation", "status", "created_at"]
    list_filter = ["status", "operation", "source_table"]
    search_fields = ["source_table", "record_uuid"]


@admin.register(SyncOperation)
class SyncOperationAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(SyncStatus)
class SyncStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
