from apps.core.constants.permissions import institutions

ACTION_PERMISSIONS = {
    "list": institutions.VIEW_SECTION,
    "get": institutions.VIEW_SECTION,
    "create": institutions.CREATE_SECTION,
    "update": institutions.UPDATE_SECTION,
    "partial_update": institutions.UPDATE_SECTION,
    "destroy": institutions.DELETE_SECTION,
}
