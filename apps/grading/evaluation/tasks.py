from .infrastructure.models import EvaluativeActivity
from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler


@register_sync_handler("evaluative_activity")
class EvaluativeActivitySyncHandler(BaseSyncHandler):
    source_table = "evaluative_activity"
    model = EvaluativeActivity
    business_key_fields = ["teacher_subject_section_id", "academic_period_id", "name"]
