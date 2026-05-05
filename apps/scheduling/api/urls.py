from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ScheduleSlotViewSet,
    ScheduleTemplateConfigViewSet,
    SubjectConstraintViewSet,
    TeacherAvailabilityViewSet,
    TimeSlotViewSet,
)

router = DefaultRouter()
router.register(r"schedule-slots", ScheduleSlotViewSet, basename="schedule-slot")
router.register(r"time-slots", TimeSlotViewSet, basename="time-slot")
router.register(
    r"teacher-availability",
    TeacherAvailabilityViewSet,
    basename="teacher-availability",
)
router.register(
    r"subject-constraints",
    SubjectConstraintViewSet,
    basename="subject-constraint",
)
router.register(
    r"schedule-configs",
    ScheduleTemplateConfigViewSet,
    basename="schedule-config",
)

urlpatterns = [
    path("", include(router.urls)),
]
