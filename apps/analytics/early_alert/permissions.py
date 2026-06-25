"""
Permisos para el módulo de alertas tempranas.

Mapea acciones del ViewSet a códigos de permiso del sistema.
"""

from apps.core.constants.permissions import analytics

ACTION_PERMISSIONS = {
    "list": analytics.VIEW_EARLY_ALERT,
    "get": analytics.VIEW_EARLY_ALERT,
    "mark_attended": analytics.UPDATE_EARLY_ALERT,
}
