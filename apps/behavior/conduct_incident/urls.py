from apps.behavior.api.routers import BehaviorRouter

from .api.views import ConductIncidentViewSet

router = BehaviorRouter()
router.register(r"conduct-incidents", ConductIncidentViewSet, basename="conduct-incident")

urlpatterns = router.urls
