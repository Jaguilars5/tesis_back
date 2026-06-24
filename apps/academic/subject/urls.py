from apps.academic.api.routers import AcademicRouter

from .api.views import SubjectViewSet

router = AcademicRouter()
router.register(r"subjects", SubjectViewSet, basename="subject")

urlpatterns = router.urls
