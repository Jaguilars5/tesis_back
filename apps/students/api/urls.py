from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EnrollmentViewSet,
    KinshipViewSet,
    SpecialNeedsTypeViewSet,
    StudentViewSet,
    StudentRepresentativeViewSet,
)

router = DefaultRouter()
router.register(r"student", StudentViewSet, basename="student")
router.register(
    r"student-representative",
    StudentRepresentativeViewSet,
    basename="student-representative",
)
router.register(
    r"enrollments",
    EnrollmentViewSet,
    basename="enrollment",
)
router.register(
    r"kinship",
    KinshipViewSet,
    basename="kinship",
)
router.register(
    r"special-needs-types",
    SpecialNeedsTypeViewSet,
    basename="special-needs-type",
)

urlpatterns = [
    path("", include(router.urls)),
]
