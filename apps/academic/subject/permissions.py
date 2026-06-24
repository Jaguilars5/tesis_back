from apps.core.constants.permissions import academic

ACTION_PERMISSIONS = {
    "list": academic.VIEW_SUBJECT,
    "get": academic.VIEW_SUBJECT,
    "create": academic.CREATE_SUBJECT,
    "update": academic.UPDATE_SUBJECT,
    "partial_update": academic.UPDATE_SUBJECT,
    "destroy": academic.DELETE_SUBJECT,
    "soft_delete": academic.DELETE_SUBJECT,
}
