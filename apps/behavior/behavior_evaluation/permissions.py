from apps.core.constants.permissions import behavior

ACTION_PERMISSIONS = {
    "list": behavior.VIEW_BEHAVIOR_EVALUATION,
    "get": behavior.VIEW_BEHAVIOR_EVALUATION,
    "create": behavior.CREATE_BEHAVIOR_EVALUATION,
    "update": behavior.UPDATE_BEHAVIOR_EVALUATION,
    "partial_update": behavior.UPDATE_BEHAVIOR_EVALUATION,
    "destroy": behavior.DELETE_BEHAVIOR_EVALUATION,
    "calculate": behavior.CREATE_BEHAVIOR_EVALUATION,
    "related_incidents": behavior.VIEW_BEHAVIOR_EVALUATION,
}
