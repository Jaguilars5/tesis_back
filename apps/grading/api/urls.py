from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AttendanceStatusViewSet,
    AttendanceViewSet,
    BehaviorEvaluationViewSet,
    ClassAssignmentViewSet,
    ConductIncidentViewSet,
    EvaluationCriteriaViewSet,
    EvaluationMacroViewSet,
    EvaluationSubcriteriaViewSet,
    GradeChangeHistoryViewSet,
    GradeTypeViewSet,
    QualitativeScaleViewSet,
    StudentNoteViewSet,
)

router = DefaultRouter()
router.register(r"student-notes", StudentNoteViewSet, basename="student-note")
router.register(r"attendance", AttendanceViewSet, basename="attendance")
router.register(r"conduct-incidents", ConductIncidentViewSet, basename="conduct-incident")
router.register(r"attendance-statuses", AttendanceStatusViewSet, basename="attendance-status")
router.register(r"grade-types", GradeTypeViewSet, basename="grade-type")
router.register(r"qualitative-scales", QualitativeScaleViewSet, basename="qualitative-scale")
router.register(r"behavior-evaluations", BehaviorEvaluationViewSet, basename="behavior-evaluation")
router.register(r"evaluation-macros", EvaluationMacroViewSet, basename="evaluation-macro")
router.register(r"evaluation-criteria", EvaluationCriteriaViewSet, basename="evaluation-criteria")
router.register(r"evaluation-subcriteria", EvaluationSubcriteriaViewSet, basename="evaluation-subcriteria")
router.register(r"class-assignments", ClassAssignmentViewSet, basename="class-assignment")
router.register(r"grade-history", GradeChangeHistoryViewSet, basename="grade-history")

urlpatterns = [
    path("", include(router.urls)),
]
