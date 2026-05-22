from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SectionViewSet, SubjectViewSet,
    AcademicPeriodViewSet,
    TeacherSubjectSectionViewSet, SubjectAcademicConfigViewSet,
    SubjectOfferingViewSet,
)

router = DefaultRouter()
router.register(r'section', SectionViewSet, basename='section')
router.register(r'subject', SubjectViewSet, basename='subject')
router.register(r'academic-period', AcademicPeriodViewSet, basename='academic-period')
router.register(r'teacher-subject-section', TeacherSubjectSectionViewSet, basename='teacher-subject-section')
router.register(r'subject-academic-configs', SubjectAcademicConfigViewSet, basename='subject-academic-config')
router.register(r'subject-offerings', SubjectOfferingViewSet, basename='subject-offering')

urlpatterns = [
    path('', include(router.urls)),
]
