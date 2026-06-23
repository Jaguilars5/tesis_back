from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AcademicPeriodViewSet,
    ClassScheduleViewSet,
    PeriodTypeViewSet,
    SubjectAcademicConfigViewSet,
    SubjectOfferingViewSet,
    SubjectViewSet,
    TeacherSubjectSectionViewSet,
)

router = DefaultRouter()
router.register(r"subject", SubjectViewSet, basename="subject")
router.register(r"academic-period", AcademicPeriodViewSet, basename="academic-period")
router.register(
    r"teacher-subject-section",
    TeacherSubjectSectionViewSet,
    basename="teacher-subject-section",
)
router.register(
    r"subject-academic-configs",
    SubjectAcademicConfigViewSet,
    basename="subject-academic-config",
)
router.register(
    r"subject-offerings", SubjectOfferingViewSet, basename="subject-offering"
)
router.register(r"period-types", PeriodTypeViewSet, basename="period-type")
router.register(r"class-schedule", ClassScheduleViewSet, basename="class-schedule")

urlpatterns = [
    path("", include(router.urls)),
]
