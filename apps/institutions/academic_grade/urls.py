from apps.institutions.api.routers import InstitutionsRouter

from .api.views import AcademicGradeViewSet

router = InstitutionsRouter()
router.register(r"academic-grades", AcademicGradeViewSet, basename="institutions-academic-grade")

urlpatterns = router.urls
