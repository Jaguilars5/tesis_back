from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InstitutionViewSet, SchoolYearViewSet, ClassroomViewSet

router = DefaultRouter()
router.register(r"institution", InstitutionViewSet, basename="institution")
router.register(r"school-year", SchoolYearViewSet, basename="school-year")
router.register(r"classroom", ClassroomViewSet, basename="classroom")

urlpatterns = [
    path("", include(router.urls)),
]
