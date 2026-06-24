from apps.core.constants.permissions import institutions

ACTION_PERMISSIONS = {
    "list": institutions.VIEW_SCHOOL_YEAR,
    "get": institutions.VIEW_SCHOOL_YEAR,
    "create": institutions.CREATE_SCHOOL_YEAR,
    "update": institutions.UPDATE_SCHOOL_YEAR,
    "partial_update": institutions.UPDATE_SCHOOL_YEAR,
    "destroy": institutions.DELETE_SCHOOL_YEAR,
}
