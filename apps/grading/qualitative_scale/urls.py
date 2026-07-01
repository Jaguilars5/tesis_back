from apps.grading.api.routers import GradingRouter

from .api.views import QualitativeScaleViewSet

router = GradingRouter()
router.register(r"qualitative-scales", QualitativeScaleViewSet, basename="qualitative-scale")

urlpatterns = router.urls
