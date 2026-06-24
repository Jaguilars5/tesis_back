from apps.grading.api.routers import GradingRouter

from .api.views import (
    StudentNoteViewSet,
    GradeChangeHistoryViewSet,
    PeriodGradeSummaryViewSet,
)

router = GradingRouter()
router.register(r"student-notes", StudentNoteViewSet, basename="student-note")
router.register(r"grade-history", GradeChangeHistoryViewSet, basename="grade-history")
router.register(r"period-grade-summaries", PeriodGradeSummaryViewSet, basename="period-grade-summary")

urlpatterns = router.urls
