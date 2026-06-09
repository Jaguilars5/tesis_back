from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ActivityTypeViewSet,
    BlockComponentViewSet,
    ComponentIndicatorViewSet,
    EvaluationBlockViewSet,
    EvaluationTypeViewSet,
    EvaluativeActivityViewSet,
    GradeChangeHistoryViewSet,
    GradeTypeViewSet,
    PeriodGradeSummaryViewSet,
    ProjectNoteViewSet,
    PromotionStatusViewSet,
    QualitativeScaleViewSet,
    RecoveryProcessTypeViewSet,
    RecoveryProcessViewSet,
    StudentNoteViewSet,
)

router = DefaultRouter()
router.register(r"student-notes", StudentNoteViewSet, basename="student-note")
router.register(
    r"evaluation-blocks", EvaluationBlockViewSet, basename="evaluation-block"
)
router.register(r"block-components", BlockComponentViewSet, basename="block-component")
router.register(
    r"component-indicators", ComponentIndicatorViewSet, basename="component-indicator"
)
router.register(
    r"evaluative-activities", EvaluativeActivityViewSet, basename="evaluative-activity"
)
router.register(r"grade-history", GradeChangeHistoryViewSet, basename="grade-history")
router.register(
    r"period-grade-summaries",
    PeriodGradeSummaryViewSet,
    basename="period-grade-summary",
)
router.register(
    r"recovery-processes", RecoveryProcessViewSet, basename="recovery-process"
)
router.register(r"project-notes", ProjectNoteViewSet, basename="project-note")
router.register(r"grade-types", GradeTypeViewSet, basename="grade-type")
router.register(r"qualitative-scales", QualitativeScaleViewSet, basename="qualitative-scale")
router.register(r"evaluation-types", EvaluationTypeViewSet, basename="evaluation-type")
router.register(r"activity-types", ActivityTypeViewSet, basename="activity-type")
router.register(r"promotion-statuses", PromotionStatusViewSet, basename="promotion-status")
router.register(r"recovery-process-types", RecoveryProcessTypeViewSet, basename="recovery-process-type")

urlpatterns = [
    path("", include(router.urls)),
]
