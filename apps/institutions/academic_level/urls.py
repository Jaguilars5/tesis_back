from apps.institutions.api.routers import InstitutionsRouter

from .api.views import AcademicLevelViewSet

router = InstitutionsRouter()
router.register(r"academic-levels", AcademicLevelViewSet, basename="academic-level")

urlpatterns = router.urls
