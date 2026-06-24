from apps.core.constants.permissions import academic

ACTION_PERMISSIONS = {
    "list": academic.VIEW_SUBJECT_CONFIG,
    "get": academic.VIEW_SUBJECT_CONFIG,
    "create": academic.CREATE_SUBJECT_CONFIG,
    "update": academic.UPDATE_SUBJECT_CONFIG,
    "partial_update": academic.UPDATE_SUBJECT_CONFIG,
    "destroy": academic.DELETE_SUBJECT_CONFIG,
    "soft_delete": academic.DELETE_SUBJECT_CONFIG,
}
