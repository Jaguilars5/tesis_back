from apps.core.constants.permissions import academic

ACTION_PERMISSIONS = {
    "list": academic.VIEW_CLASS_SCHEDULE,
    "get": academic.VIEW_CLASS_SCHEDULE,
    "create": academic.CREATE_CLASS_SCHEDULE,
    "update": academic.UPDATE_CLASS_SCHEDULE,
    "partial_update": academic.UPDATE_CLASS_SCHEDULE,
    "destroy": academic.DELETE_CLASS_SCHEDULE,
    "soft_delete": academic.DELETE_CLASS_SCHEDULE,
    "by_section": academic.VIEW_CLASS_SCHEDULE,
    "my_schedule": None,
    "my_today": None,
}
