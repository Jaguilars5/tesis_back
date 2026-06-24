from apps.attendance.api.routers import AttendanceRouter

from .api.views import AttendanceStatusViewSet

router = AttendanceRouter()
router.register(r"attendance-statuses", AttendanceStatusViewSet, basename="attendance-status")

urlpatterns = router.urls
