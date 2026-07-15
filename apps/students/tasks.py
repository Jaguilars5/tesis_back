from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler
from apps.students.models import Enrollment


@register_sync_handler("enrollment")
class EnrollmentSyncHandler(BaseSyncHandler):
    source_table = "enrollment"
    model = Enrollment
    business_key_fields = ["student_id", "teacher_subject_section_id", "academic_period_id"]
