from apps.attendance.api.routers import AttendanceRouter

from .api.views import AbsenceTypeViewSet

router = AttendanceRouter()
router.register(r"absence-types", AbsenceTypeViewSet, basename="absence-type")

urlpatterns = router.urls
