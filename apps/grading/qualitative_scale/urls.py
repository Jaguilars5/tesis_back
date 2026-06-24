from apps.grading.api.routers import GradingRouter

from .api.views import QualitativeScaleViewSet, QualitativeScaleSublevelViewSet

router = GradingRouter()
router.register(r"qualitative-scales", QualitativeScaleViewSet, basename="qualitative-scale")
router.register(r"qualitative-scale-sublevels", QualitativeScaleSublevelViewSet, basename="qualitative-scale-sublevel")

urlpatterns = router.urls
