"""
Configuración de la aplicación Analytics.
"""

from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """
    Configuración de Django para el módulo de analítica y predicción de riesgo.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analytics"
