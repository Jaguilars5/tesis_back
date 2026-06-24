from apps.institutions.api.routers import InstitutionsRouter

from .api.views import SectionViewSet

router = InstitutionsRouter()
router.register(r"section", SectionViewSet, basename="section")

urlpatterns = router.urls
