from rest_framework.routers import DefaultRouter
from apps.attendance.api.views import (
    AbsenceTypeViewSet,
    AttendanceStatusViewSet,
    AttendanceViewSet,
)

router = DefaultRouter()
router.register(r"attendances", AttendanceViewSet, basename="attendance")
router.register(r"attendance-statuses", AttendanceStatusViewSet, basename="attendance-status")
router.register(r"absence-types", AbsenceTypeViewSet, basename="absence-type")

urlpatterns = router.urls
