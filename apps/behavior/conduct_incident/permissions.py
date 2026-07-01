from apps.core.constants.permissions import behavior

ACTION_PERMISSIONS = {
    "list": behavior.VIEW_CONDUCT_INCIDENT,
    "get": behavior.VIEW_CONDUCT_INCIDENT,
    "create": behavior.CREATE_CONDUCT_INCIDENT,
    "update": behavior.UPDATE_CONDUCT_INCIDENT,
    "partial_update": behavior.UPDATE_CONDUCT_INCIDENT,
    "destroy": behavior.DELETE_CONDUCT_INCIDENT,
    "soft_delete": behavior.DELETE_CONDUCT_INCIDENT,
    "replicate_push": behavior.CREATE_CONDUCT_INCIDENT,
    "replicate_changes": behavior.VIEW_CONDUCT_INCIDENT,
}
