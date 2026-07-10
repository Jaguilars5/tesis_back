from apps.core.constants.permissions import attendance

ACTION_PERMISSIONS = {
    "list": attendance.VIEW_ATTENDANCE,
    "get": attendance.VIEW_ATTENDANCE,
    "create": attendance.CREATE_ATTENDANCE,
    "update": attendance.UPDATE_ATTENDANCE,
    "partial_update": attendance.UPDATE_ATTENDANCE,
    "destroy": attendance.DELETE_ATTENDANCE,
    "soft_delete": attendance.DELETE_ATTENDANCE,
    "batch_create": attendance.CREATE_ATTENDANCE,
    "take_by_schedule": attendance.CREATE_ATTENDANCE,
    "session": attendance.VIEW_ATTENDANCE,
    "replicate_push": attendance.CREATE_ATTENDANCE,
    "replicate_changes": attendance.VIEW_ATTENDANCE,
    "summary": attendance.VIEW_ATTENDANCE,
}
