from apps.core.constants.permissions import attendance

ACTION_PERMISSIONS = {
    "list": attendance.VIEW_ATTENDANCE,
    "get": attendance.VIEW_ATTENDANCE,
    "create": attendance.CREATE_ATTENDANCE,
    "update": attendance.UPDATE_ATTENDANCE,
    "partial_update": attendance.UPDATE_ATTENDANCE,
    "destroy": attendance.DELETE_ATTENDANCE,
    "batch_create": attendance.CREATE_ATTENDANCE,
    "take_by_schedule": attendance.CREATE_ATTENDANCE,
}
