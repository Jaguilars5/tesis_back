from apps.grading.api.routers import GradingRouter

from .api.views import ActivityTypeViewSet

router = GradingRouter()
router.register(r"activity-types", ActivityTypeViewSet, basename="activity-type")

urlpatterns = router.urls
