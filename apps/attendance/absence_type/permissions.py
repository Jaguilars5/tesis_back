from apps.core.constants.permissions import attendance

ACTION_PERMISSIONS = {
    "list": attendance.VIEW_ABSENCE_TYPE,
    "get": attendance.VIEW_ABSENCE_TYPE,
    "create": attendance.CREATE_ABSENCE_TYPE,
    "update": attendance.UPDATE_ABSENCE_TYPE,
    "partial_update": attendance.UPDATE_ABSENCE_TYPE,
    "destroy": attendance.DELETE_ABSENCE_TYPE,
}
