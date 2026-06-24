from apps.academic.api.routers import AcademicRouter

from .api.views import PeriodTypeViewSet

router = AcademicRouter()
router.register(r"period-types", PeriodTypeViewSet, basename="period-type")

urlpatterns = router.urls
