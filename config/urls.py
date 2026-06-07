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

API_MODULES = [
    "accounts",
    "academic",
    "institutions",
    "grading",
    "students",
    "analytics",
    "attendance",
    "core",
]

urlpatterns = [
    path("admin/", admin.site.urls),
    # API Routes
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/academic/", include("apps.academic.urls")),
    path("api/institutions/", include("apps.institutions.urls")),
    path("api/grading/", include("apps.grading.urls")),
    path("api/students/", include("apps.students.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/attendance/", include("apps.attendance.urls")),
    path("api/core/", include("apps.core.urls")),
    # OpenAPI Schema completo (público)
    path(
        "api/schema/",
        SpectacularAPIView.as_view(permission_classes=[AllowAny]),
        name="schema",
    ),
    # Swagger UI completo (público)
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema", permission_classes=[AllowAny]
        ),
        name="swagger-ui",
    ),
    # ReDoc completo (público)
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema", permission_classes=[AllowAny]),
        name="redoc",
    ),
]

# ── Schema, Swagger UI y ReDoc por módulo ──────────────────────────────────
for mod in API_MODULES:
    # Construye patrones URL reales (URLResolver) para filtrar el schema.
    # patterns NO acepta strings, necesita objetos URLPattern/URLResolver.
    module_patterns = [path(f"api/{mod}/", include(f"apps.{mod}.urls"))]

    # Schema OpenAPI filtrado por módulo
    urlpatterns.append(
        path(
            f"api/schema/{mod}/",
            SpectacularAPIView.as_view(
                permission_classes=[AllowAny],
                patterns=module_patterns,
            ),
            name=f"schema-{mod}",
        ),
    )
    # Swagger UI del módulo
    urlpatterns.append(
        path(
            f"api/docs/{mod}/",
            SpectacularSwaggerView.as_view(
                url_name=f"schema-{mod}",
                permission_classes=[AllowAny],
            ),
            name=f"swagger-ui-{mod}",
        ),
    )
    # ReDoc del módulo
    urlpatterns.append(
        path(
            f"api/redoc/{mod}/",
            SpectacularRedocView.as_view(
                url_name=f"schema-{mod}",
                permission_classes=[AllowAny],
            ),
            name=f"redoc-{mod}",
        ),
    )
