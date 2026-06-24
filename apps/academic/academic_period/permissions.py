from apps.core.constants.permissions import academic

ACTION_PERMISSIONS = {
    "list": academic.VIEW_PERIOD,
    "get": academic.VIEW_PERIOD,
    "create": academic.CREATE_PERIOD,
    "update": academic.UPDATE_PERIOD,
    "partial_update": academic.UPDATE_PERIOD,
    "destroy": academic.DELETE_PERIOD,
    "soft_delete": academic.DELETE_PERIOD,
}
