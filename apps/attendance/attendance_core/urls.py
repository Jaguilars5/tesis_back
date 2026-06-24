from apps.attendance.api.routers import AttendanceRouter

from .api.views import AttendanceViewSet

router = AttendanceRouter()
router.register(r"attendances", AttendanceViewSet, basename="attendance")

urlpatterns = router.urls
