from apps.grading.api.routers import GradingRouter

from .api.views import (
    StudentNoteViewSet,
    GradeChangeHistoryViewSet,
    PeriodGradeSummaryViewSet,
    AnnualGradeSummaryViewSet,
)

router = GradingRouter()
router.register(r"student-notes", StudentNoteViewSet, basename="student-note")
router.register(r"grade-history", GradeChangeHistoryViewSet, basename="grade-history")
router.register(r"period-grade-summaries", PeriodGradeSummaryViewSet, basename="period-grade-summary")
router.register(r"annual-grade-summaries", AnnualGradeSummaryViewSet, basename="annual-grade-summary")

urlpatterns = router.urls
