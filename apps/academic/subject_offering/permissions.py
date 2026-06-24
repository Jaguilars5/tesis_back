from apps.core.constants.permissions import academic

ACTION_PERMISSIONS = {
    "list": academic.VIEW_SUBJECT_OFFERING,
    "get": academic.VIEW_SUBJECT_OFFERING,
    "create": academic.CREATE_SUBJECT_OFFERING,
    "update": academic.UPDATE_SUBJECT_OFFERING,
    "partial_update": academic.UPDATE_SUBJECT_OFFERING,
    "destroy": academic.DELETE_SUBJECT_OFFERING,
    "soft_delete": academic.DELETE_SUBJECT_OFFERING,
}
