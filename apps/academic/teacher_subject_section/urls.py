from apps.academic.api.routers import AcademicRouter

from .api.views import TeacherSubjectSectionViewSet

router = AcademicRouter()
router.register(
    r"teacher-subject-sections",
    TeacherSubjectSectionViewSet,
    basename="teacher-subject-section",
)

urlpatterns = router.urls
