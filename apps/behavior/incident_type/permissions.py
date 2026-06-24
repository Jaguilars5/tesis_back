from apps.core.constants.permissions import behavior

ACTION_PERMISSIONS = {
    "list": behavior.VIEW_INCIDENT_TYPE,
    "get": behavior.VIEW_INCIDENT_TYPE,
    "create": behavior.CREATE_INCIDENT_TYPE,
    "update": behavior.UPDATE_INCIDENT_TYPE,
    "partial_update": behavior.UPDATE_INCIDENT_TYPE,
    "destroy": behavior.DELETE_INCIDENT_TYPE,
    "soft_delete": behavior.DELETE_INCIDENT_TYPE,
}
