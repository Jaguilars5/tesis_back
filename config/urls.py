"""
URL configuration for backend project.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import AllowAny

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

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
    # OpenAPI Schema (público)
    path(
        "api/schema/",
        SpectacularAPIView.as_view(permission_classes=[AllowAny]),
        name="schema",
    ),
    # Swagger UI (público)
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema", permission_classes=[AllowAny]),
        name="swagger-ui",
    ),
    # ReDoc UI (público)
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema", permission_classes=[AllowAny]),
        name="redoc",
    ),
]



