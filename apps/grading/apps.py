"""
Configuración de la aplicación Grading.
"""

from django.apps import AppConfig


class GradingConfig(AppConfig):
    """
    Configuración específica de Django para el módulo de calificaciones.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.grading"

    def ready(self):
        from . import signals  # noqa: F401  registra receivers de StudentNote

