from apps.core.constants.permissions import attendance

ACTION_PERMISSIONS = {
    "list": attendance.VIEW_ATTENDANCE_STATUS,
    "get": attendance.VIEW_ATTENDANCE_STATUS,
    "create": attendance.CREATE_ATTENDANCE_STATUS,
    "update": attendance.UPDATE_ATTENDANCE_STATUS,
    "partial_update": attendance.UPDATE_ATTENDANCE_STATUS,
    "destroy": attendance.DELETE_ATTENDANCE_STATUS,
}
