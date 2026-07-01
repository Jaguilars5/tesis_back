from apps.core.constants.permissions import grading

ACTION_PERMISSIONS = {
    "list": grading.VIEW_NOTE,
    "get": grading.VIEW_NOTE,
    "create": grading.CREATE_NOTE,
    "update": grading.UPDATE_NOTE,
    "partial_update": grading.UPDATE_NOTE,
    "destroy": grading.DELETE_NOTE,
    "soft_delete": grading.DELETE_NOTE,
    "take_by_activity": grading.CREATE_NOTE,
    "replicate_push": grading.CREATE_NOTE,
    "replicate_changes": grading.VIEW_NOTE,
}

GRADE_HISTORY_PERMISSIONS = {
    "list": grading.VIEW_GRADE_HISTORY,
    "get": grading.VIEW_GRADE_HISTORY,
}

GRADE_SUMMARY_PERMISSIONS = {
    "list": grading.VIEW_GRADE_SUMMARY,
    "get": grading.VIEW_GRADE_SUMMARY,
    "create": grading.CREATE_GRADE_SUMMARY,
    "update": grading.UPDATE_GRADE_SUMMARY,
    "partial_update": grading.UPDATE_GRADE_SUMMARY,
    "destroy": grading.DELETE_GRADE_SUMMARY,
    "recalculate": grading.RECALCULATE_GRADE_SUMMARY,
    "recalculate_period": grading.RECALCULATE_GRADE_SUMMARY,
}
