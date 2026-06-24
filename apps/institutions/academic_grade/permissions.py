from apps.core.constants.permissions import institutions

ACTION_PERMISSIONS = {
    "list": institutions.VIEW_ACADEMIC_GRADE,
    "get": institutions.VIEW_ACADEMIC_GRADE,
    "create": institutions.CREATE_ACADEMIC_GRADE,
    "update": institutions.UPDATE_ACADEMIC_GRADE,
    "destroy": institutions.DELETE_ACADEMIC_GRADE,
    "soft_delete": institutions.DELETE_ACADEMIC_GRADE,
}
