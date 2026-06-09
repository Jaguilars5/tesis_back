from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AcademicGradeViewSet,
    AcademicLevelViewSet,
    AcademicSublevelViewSet,
    SchoolYearViewSet,
    SectionViewSet,
)

router = DefaultRouter()
router.register(r"school-year", SchoolYearViewSet, basename="school-year")
router.register(r"academic-levels", AcademicLevelViewSet, basename="academic-level")
router.register(r"academic-sublevel", AcademicSublevelViewSet, basename="academic-sublevel")
router.register(r"academic-grades", AcademicGradeViewSet, basename="academic-grade")
router.register(r"section", SectionViewSet, basename="section")

urlpatterns = [
    path("", include(router.urls)),
]
