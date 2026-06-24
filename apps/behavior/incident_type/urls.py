from apps.behavior.api.routers import BehaviorRouter

from .api.views import IncidentTypeViewSet

router = BehaviorRouter()
router.register(r"incident-types", IncidentTypeViewSet, basename="incident-type")

urlpatterns = router.urls
