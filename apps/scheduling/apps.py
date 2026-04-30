"""
Configuración de la aplicación Scheduling.
"""

from django.apps import AppConfig


class SchedulingConfig(AppConfig):
    """
    Configuración específica de Django para el módulo de horarios.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.scheduling"
