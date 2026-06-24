from apps.academic.api.routers import AcademicRouter

from .api.views import ClassScheduleViewSet

router = AcademicRouter()
router.register(r"class-schedules", ClassScheduleViewSet, basename="class-schedule")

urlpatterns = router.urls
