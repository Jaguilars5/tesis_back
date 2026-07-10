from apps.core.constants.permissions import people as perm


CITY_ACTION_PERMISSIONS = {
    "list": None,
    "get": perm.VIEW_CITY,
}

DOCUMENT_TYPE_ACTION_PERMISSIONS = {
    "list": None,
    "get": perm.VIEW_DOCUMENT_TYPE,
    "create": perm.CREATE_DOCUMENT_TYPE,
    "update": perm.UPDATE_DOCUMENT_TYPE,
    "partial_update": perm.UPDATE_DOCUMENT_TYPE,
    "destroy": perm.DELETE_DOCUMENT_TYPE,
    "soft_delete": perm.DELETE_DOCUMENT_TYPE,
}

PARISH_ACTION_PERMISSIONS = {
    "list": None,
    "get": perm.VIEW_PARISH,
    "create": perm.CREATE_PARISH,
    "update": perm.UPDATE_PARISH,
    "partial_update": perm.UPDATE_PARISH,
    "destroy": perm.DELETE_PARISH,
    "soft_delete": perm.DELETE_PARISH,
}

PERSON_ACTION_PERMISSIONS = {
    "list": perm.VIEW_PERSON,
    "get": perm.VIEW_PERSON,
    "create": perm.CREATE_PERSON,
    "update": perm.UPDATE_PERSON,
    "partial_update": perm.UPDATE_PERSON,
    "destroy": perm.DELETE_PERSON,
    "soft_delete": perm.DELETE_PERSON,
}
