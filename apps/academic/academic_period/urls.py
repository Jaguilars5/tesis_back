from apps.academic.api.routers import AcademicRouter

from .api.views import AcademicPeriodViewSet

router = AcademicRouter()
router.register(r"academic-periods", AcademicPeriodViewSet, basename="academic-period")

urlpatterns = router.urls
