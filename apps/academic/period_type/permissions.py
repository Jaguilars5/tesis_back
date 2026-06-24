from apps.core.constants.permissions import academic

ACTION_PERMISSIONS = {
    "list": academic.VIEW_PERIOD_TYPE,
    "get": academic.VIEW_PERIOD_TYPE,
    "create": academic.CREATE_PERIOD_TYPE,
    "update": academic.UPDATE_PERIOD_TYPE,
    "partial_update": academic.UPDATE_PERIOD_TYPE,
    "destroy": academic.DELETE_PERIOD_TYPE,
    "soft_delete": academic.DELETE_PERIOD_TYPE,
}
