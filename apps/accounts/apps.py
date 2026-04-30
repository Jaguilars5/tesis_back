"""
Configuración del módulo accounts.

Registra la app con Django y conecta señales.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuración de la aplicación accounts."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
    verbose_name = "Gestión de Cuentas y Permisos"

    def ready(self):
        """Se ejecuta cuando Django carga la aplicación."""
        # Importar señales si existen
        try:
            from . import signals  # noqa
        except ImportError:
            pass
