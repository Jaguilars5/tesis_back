from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AttendanceViewSet, ConductIncidentViewSet, StudentNoteViewSet

router = DefaultRouter()
router.register(r"student-notes", StudentNoteViewSet, basename="student-note")
router.register(r"attendance", AttendanceViewSet, basename="attendance")
router.register(r"conduct-incidents", ConductIncidentViewSet, basename="conduct-incident")

urlpatterns = [
    path("", include(router.urls)),
]
