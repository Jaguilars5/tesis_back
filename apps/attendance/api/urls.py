from django.urls import path, include

urlpatterns = [
    path("", include("apps.attendance.absence_type.urls")),
    path("", include("apps.attendance.attendance_status.urls")),
    path("", include("apps.attendance.attendance_core.urls")),
]
