from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SectionViewSet, SubjectViewSet, ConfigAcademicViewSet,
    AcademicPeriodViewSet, AcademicActivityViewSet, TimingRegimeViewSet,
    TeacherSubjectSectionViewSet
)

router = DefaultRouter()
router.register(r'section', SectionViewSet, basename='section')
router.register(r'subject', SubjectViewSet, basename='subject')
router.register(r'config-academic', ConfigAcademicViewSet, basename='config-academic')
router.register(r'academic-period', AcademicPeriodViewSet, basename='academic-period')
router.register(r'academic-activity', AcademicActivityViewSet, basename='academic-activity')
router.register(r'timing-regime', TimingRegimeViewSet, basename='timing-regime')
router.register(r'teacher-subject-section', TeacherSubjectSectionViewSet, basename='teacher-subject-section')

urlpatterns = [
    path('', include(router.urls)),
]
