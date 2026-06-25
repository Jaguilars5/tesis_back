from apps.core.constants.permissions import institutions

ACTION_PERMISSIONS = {
    "list": institutions.VIEW_ACADEMIC_LEVEL,
    "get": institutions.VIEW_ACADEMIC_LEVEL,
    "create": institutions.CREATE_ACADEMIC_LEVEL,
    "update": institutions.UPDATE_ACADEMIC_LEVEL,
    "partial_update": institutions.UPDATE_ACADEMIC_LEVEL,
    "destroy": institutions.DELETE_ACADEMIC_LEVEL,
    "soft_delete": institutions.DELETE_ACADEMIC_LEVEL,
}
