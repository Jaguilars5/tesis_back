from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, RepresentativeViewSet, StudentRepresentativeViewSet

app_name = "students-api"

router = DefaultRouter()
router.register(r"student", StudentViewSet, basename="student")
router.register(r"representative", RepresentativeViewSet, basename="representative")
router.register(
    r"student-representative",
    StudentRepresentativeViewSet,
    basename="student-representative",
)

urlpatterns = [
    path("", include(router.urls)),
]
