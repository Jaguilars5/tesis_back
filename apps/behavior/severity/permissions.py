from apps.core.constants.permissions import behavior

ACTION_PERMISSIONS = {
    "list": behavior.VIEW_SEVERITY,
    "get": behavior.VIEW_SEVERITY,
    "create": behavior.CREATE_SEVERITY,
    "update": behavior.UPDATE_SEVERITY,
    "partial_update": behavior.UPDATE_SEVERITY,
    "destroy": behavior.DELETE_SEVERITY,
    "soft_delete": behavior.DELETE_SEVERITY,
}
