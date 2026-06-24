from apps.core.constants.permissions import institutions

ACTION_PERMISSIONS = {
    "list": institutions.VIEW_ACADEMIC_SUBLEVEL,
    "get": institutions.VIEW_ACADEMIC_SUBLEVEL,
    "create": institutions.CREATE_ACADEMIC_SUBLEVEL,
    "update": institutions.UPDATE_ACADEMIC_SUBLEVEL,
    "partial_update": institutions.UPDATE_ACADEMIC_SUBLEVEL,
    "destroy": institutions.DELETE_ACADEMIC_SUBLEVEL,
}
