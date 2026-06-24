from apps.institutions.api.routers import InstitutionsRouter

from .api.views import AcademicSublevelViewSet

router = InstitutionsRouter()
router.register(r"academic-sublevel", AcademicSublevelViewSet, basename="academic-sublevel")

urlpatterns = router.urls
