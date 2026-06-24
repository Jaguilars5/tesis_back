from apps.academic.api.routers import AcademicRouter

from .api.views import SubjectOfferingViewSet

router = AcademicRouter()
router.register(r"subject-offerings", SubjectOfferingViewSet, basename="subject-offering")

urlpatterns = router.urls
