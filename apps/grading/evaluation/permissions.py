from apps.core.constants.permissions import grading

ACTION_PERMISSIONS = {
    "list": grading.VIEW_EVALUATION_BLOCK,
    "get": grading.VIEW_EVALUATION_BLOCK,
    "create": grading.CREATE_EVALUATION_BLOCK,
    "update": grading.UPDATE_EVALUATION_BLOCK,
    "partial_update": grading.UPDATE_EVALUATION_BLOCK,
    "destroy": grading.DELETE_EVALUATION_BLOCK,
    "soft_delete": grading.DELETE_EVALUATION_BLOCK,
}

BLOCK_COMPONENT_PERMISSIONS = {
    "list": grading.VIEW_BLOCK_COMPONENT,
    "get": grading.VIEW_BLOCK_COMPONENT,
    "by_teacher_subject_section": grading.VIEW_BLOCK_COMPONENT,
    "create": grading.CREATE_BLOCK_COMPONENT,
    "update": grading.UPDATE_BLOCK_COMPONENT,
    "partial_update": grading.UPDATE_BLOCK_COMPONENT,
    "destroy": grading.DELETE_BLOCK_COMPONENT,
    "soft_delete": grading.DELETE_BLOCK_COMPONENT,
}

EVALUATIVE_ACTIVITY_PERMISSIONS = {
    "list": grading.VIEW_EVALUATIVE_ACTIVITY,
    "get": grading.VIEW_EVALUATIVE_ACTIVITY,
    "create": grading.CREATE_EVALUATIVE_ACTIVITY,
    "update": grading.UPDATE_EVALUATIVE_ACTIVITY,
    "partial_update": grading.UPDATE_EVALUATIVE_ACTIVITY,
    "destroy": grading.DELETE_EVALUATIVE_ACTIVITY,
    "soft_delete": grading.DELETE_EVALUATIVE_ACTIVITY,
}
