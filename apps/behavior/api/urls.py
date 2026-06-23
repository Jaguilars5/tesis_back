from rest_framework.routers import DefaultRouter
from .views import (
    BehaviorEvaluationViewSet,
    ConductIncidentViewSet,
    IncidentTypeViewSet,
    SeverityViewSet,
)

router = DefaultRouter()
router.register(r"conduct-incidents", ConductIncidentViewSet, basename="conduct-incident")
router.register(r"behavior-evaluations", BehaviorEvaluationViewSet, basename="behavior-evaluation")
router.register(r"incident-types", IncidentTypeViewSet, basename="incident-type")
router.register(r"severities", SeverityViewSet, basename="severity")

urlpatterns = router.urls