from apps.integration.tasks.sync_tasks import BaseSyncHandler, register_sync_handler
from apps.grading.models import (
    StudentNote, ProjectNote, EvaluativeActivity,
    RecoveryProcess, RecoverySession, LearningReport,
)


@register_sync_handler("student_note")
class StudentNoteSyncHandler(BaseSyncHandler):
    source_table = "student_note"
    model = StudentNote


@register_sync_handler("project_note")
class ProjectNoteSyncHandler(BaseSyncHandler):
    source_table = "project_note"
    model = ProjectNote


@register_sync_handler("evaluative_activity")
class EvaluativeActivitySyncHandler(BaseSyncHandler):
    source_table = "evaluative_activity"
    model = EvaluativeActivity


@register_sync_handler("recovery_process")
class RecoveryProcessSyncHandler(BaseSyncHandler):
    source_table = "recovery_process"
    model = RecoveryProcess


@register_sync_handler("recovery_session")
class RecoverySessionSyncHandler(BaseSyncHandler):
    source_table = "recovery_session"
    model = RecoverySession


@register_sync_handler("learning_report")
class LearningReportSyncHandler(BaseSyncHandler):
    source_table = "learning_report"
    model = LearningReport
