from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnrollmentStatusViewSet, EnrollmentViewSet, StudentViewSet, StudentRepresentativeViewSet

router = DefaultRouter()
router.register(r"student", StudentViewSet, basename="student")
router.register(
    r"student-representative",
    StudentRepresentativeViewSet,
    basename="student-representative",
)
router.register(
    r"enrollment-statuses",
    EnrollmentStatusViewSet,
    basename="enrollment-status",
)
router.register(
    r"enrollments",
    EnrollmentViewSet,
    basename="enrollment",
)

urlpatterns = [
    path("", include(router.urls)),
]
