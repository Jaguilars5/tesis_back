"""
Agregador de rutas del módulo Analytics.

Igual que apps/academic/api/urls.py, sólo incluye las rutas de cada
bounded context (student_risk, early_alert, dashboard). Cada sub-app
registra sus ViewSets con AnalyticsRouter en su propio urls.py.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("apps.analytics.student_risk.urls")),
    path("", include("apps.analytics.early_alert.urls")),
    path("", include("apps.analytics.dashboard.urls")),
]
