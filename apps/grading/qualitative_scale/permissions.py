from apps.core.constants.permissions import grading

ACTION_PERMISSIONS = {
    "list": grading.VIEW_QUALITATIVE_SCALE,
    "get": grading.VIEW_QUALITATIVE_SCALE,
    "create": grading.CREATE_QUALITATIVE_SCALE,
    "update": grading.UPDATE_QUALITATIVE_SCALE,
    "partial_update": grading.UPDATE_QUALITATIVE_SCALE,
    "destroy": grading.DELETE_QUALITATIVE_SCALE,
}
