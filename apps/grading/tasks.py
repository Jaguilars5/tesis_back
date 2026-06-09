from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler
from apps.grading.models import StudentNote, ProjectNote


@register_sync_handler("student_note")
class StudentNoteSyncHandler(BaseSyncHandler):
    model = StudentNote


@register_sync_handler("project_note")
class ProjectNoteSyncHandler(BaseSyncHandler):
    model = ProjectNote
