from apps.institutions.api.routers import InstitutionsRouter

from .api.views import SchoolYearViewSet

router = InstitutionsRouter()
router.register(r"school-year", SchoolYearViewSet, basename="school-year")

urlpatterns = router.urls
