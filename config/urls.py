"""
URL configuration for backend project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # API Routes
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/academic/", include("apps.academic.urls")),
    path("api/institutions/", include("apps.institutions.urls")),
    path("api/grading/", include("apps.grading.urls")),
    path("api/students/", include("apps.students.urls")),
    path("api/scheduling/", include("apps.scheduling.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
]



