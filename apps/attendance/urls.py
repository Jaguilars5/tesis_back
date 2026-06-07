from rest_framework.routers import DefaultRouter
from apps.attendance.api.views import (
    AttendanceViewSet, AttendanceStatusViewSet, IncidentTypeViewSet,
    ConductIncidentViewSet, SocioemotionalSkillViewSet,
    SkillEvaluationViewSet, BehaviorEvaluationViewSet,
)

router = DefaultRouter()
router.register(r"attendances", AttendanceViewSet, basename="attendance")
router.register(r"attendance-statuses", AttendanceStatusViewSet, basename="attendance-status")
router.register(r"incident-types", IncidentTypeViewSet, basename="incident-type")
router.register(r"conduct-incidents", ConductIncidentViewSet, basename="conduct-incident")
router.register(r"socioemotional-skills", SocioemotionalSkillViewSet, basename="socioemotional-skill")
router.register(r"skill-evaluations", SkillEvaluationViewSet, basename="skill-evaluation")
router.register(r"behavior-evaluations", BehaviorEvaluationViewSet, basename="behavior-evaluation")

urlpatterns = router.urls
