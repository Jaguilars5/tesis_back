"""
Permisos para el módulo de alertas tempranas.

Mapea acciones del ViewSet a códigos de permiso del sistema.
"""

from apps.core.constants.permissions import analytics

ACTION_PERMISSIONS = {
    "list": analytics.VIEW_EARLY_ALERT,
    "get": analytics.VIEW_EARLY_ALERT,
    "mark_attended": analytics.UPDATE_EARLY_ALERT,
    # Las alertas se generan automáticamente: estas acciones responden 405,
    # pero requieren permiso para distinguir "no disponible" (405) de "sin acceso" (403).
    "create": analytics.CREATE_EARLY_ALERT,
    "update": analytics.UPDATE_EARLY_ALERT,
    "partial_update": analytics.UPDATE_EARLY_ALERT,
    "destroy": analytics.DELETE_EARLY_ALERT,
}
