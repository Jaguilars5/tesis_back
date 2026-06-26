from apps.core.constants.permissions import grading

ACTION_PERMISSIONS = {
    "list": grading.VIEW_ACTIVITY_TYPE,
    "get": grading.VIEW_ACTIVITY_TYPE,
    "create": grading.CREATE_ACTIVITY_TYPE,
    "update": grading.UPDATE_ACTIVITY_TYPE,
    "partial_update": grading.UPDATE_ACTIVITY_TYPE,
    "destroy": grading.DELETE_ACTIVITY_TYPE,
    "soft_delete": grading.DELETE_ACTIVITY_TYPE,
}
