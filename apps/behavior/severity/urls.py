from apps.behavior.api.routers import BehaviorRouter

from .api.views import SeverityViewSet

router = BehaviorRouter()
router.register(r"severities", SeverityViewSet, basename="severity")

urlpatterns = router.urls
