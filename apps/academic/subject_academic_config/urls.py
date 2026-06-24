from apps.academic.api.routers import AcademicRouter

from .api.views import SubjectAcademicConfigViewSet

router = AcademicRouter()
router.register(
    r"subject-academic-configs",
    SubjectAcademicConfigViewSet,
    basename="subject-academic-config",
)

urlpatterns = router.urls
