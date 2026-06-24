from apps.core.constants.permissions import academic

ACTION_PERMISSIONS = {
    "list": academic.VIEW_TEACHER_SUBJECT,
    "get": academic.VIEW_TEACHER_SUBJECT,
    "create": academic.CREATE_TEACHER_SUBJECT,
    "update": academic.UPDATE_TEACHER_SUBJECT,
    "partial_update": academic.UPDATE_TEACHER_SUBJECT,
    "destroy": academic.DELETE_TEACHER_SUBJECT,
    "soft_delete": academic.DELETE_TEACHER_SUBJECT,
}
