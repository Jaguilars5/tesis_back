from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AcademicGradeViewSet,
    AcademicLevelViewSet,
    ClassroomViewSet,
    DocumentTypeViewSet,
    RoomTypeViewSet,
    SchoolYearViewSet,
)

router = DefaultRouter()
router.register(r"school-year", SchoolYearViewSet, basename="school-year")
router.register(r"classroom", ClassroomViewSet, basename="classroom")
router.register(r"document-types", DocumentTypeViewSet, basename="document-type")
router.register(r"room-types", RoomTypeViewSet, basename="room-type")
router.register(r"academic-levels", AcademicLevelViewSet, basename="academic-level")
router.register(r"academic-grades", AcademicGradeViewSet, basename="academic-grade")

urlpatterns = [
    path("", include(router.urls)),
]
