from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ActivityTypeViewSet,
    BlockComponentViewSet,
    EvaluationBlockViewSet,
    EvaluativeActivityViewSet,
    GradeChangeHistoryViewSet,
    PeriodGradeSummaryViewSet,
    QualitativeScaleViewSet,
    QualitativeScaleSublevelViewSet,
    StudentNoteViewSet,
)

router = DefaultRouter()
router.register(r"student-notes", StudentNoteViewSet, basename="student-note")
router.register(
    r"evaluation-blocks", EvaluationBlockViewSet, basename="evaluation-block"
)
router.register(r"block-components", BlockComponentViewSet, basename="block-component")
router.register(
    r"evaluative-activities", EvaluativeActivityViewSet, basename="evaluative-activity"
)
router.register(r"grade-history", GradeChangeHistoryViewSet, basename="grade-history")
router.register(
    r"period-grade-summaries",
    PeriodGradeSummaryViewSet,
    basename="period-grade-summary",
)
router.register(r"qualitative-scales", QualitativeScaleViewSet, basename="qualitative-scale")
router.register(r"activity-types", ActivityTypeViewSet, basename="activity-type")
router.register(r"qualitative-scale-sublevels", QualitativeScaleSublevelViewSet, basename="qualitative-scale-sublevel")

urlpatterns = [
    path("", include(router.urls)),
]
