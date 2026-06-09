from rest_framework.routers import DefaultRouter
from .views import (
    BehaviorEvaluationViewSet,
    ConductIncidentViewSet,
    DiagnosticEvaluationViewSet,
    IncidentTypeViewSet,
    SkillEvaluationViewSet,
    SocioemotionalSkillViewSet,
)

router = DefaultRouter()
router.register(r"conduct-incidents", ConductIncidentViewSet, basename="conduct-incident")
router.register(r"socioemotional-skills", SocioemotionalSkillViewSet, basename="socioemotional-skill")
router.register(r"skill-evaluations", SkillEvaluationViewSet, basename="skill-evaluation")
router.register(r"behavior-evaluations", BehaviorEvaluationViewSet, basename="behavior-evaluation")
router.register(r"diagnostic-evaluations", DiagnosticEvaluationViewSet, basename="diagnostic-evaluation")
router.register(r"incident-types", IncidentTypeViewSet, basename="incident-type")

urlpatterns = router.urls
