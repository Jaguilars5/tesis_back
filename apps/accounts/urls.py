"""
URLs para el módulo accounts.

Incluye las rutas del API REST.
"""

from django.urls import path, include

urlpatterns = [
    # ── API REST ──────────────────────────────────────────────────────────────
    # Endpoints: GET/POST /api/accounts/permissions/, /api/accounts/roles/, /api/accounts/users/
    path("", include("apps.accounts.api.urls")),
]
