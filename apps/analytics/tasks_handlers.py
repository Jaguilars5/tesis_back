from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler
from apps.analytics.early_alert.infrastructure.models import EarlyAlert


@register_sync_handler("early_alert")
class EarlyAlertSyncHandler(BaseSyncHandler):
    source_table = "early_alert"
    model = EarlyAlert
    business_key_fields = ["enrollment_id", "academic_period_id"]
