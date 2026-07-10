from apps.core.constants.permissions import iam

PERMISSION_ACTION_PERMISSIONS = {
    "list": iam.VIEW_PERMISSION,
    "get": iam.VIEW_PERMISSION,
    "create": iam.CREATE_PERMISSION,
    "update": iam.UPDATE_PERMISSION,
    "partial_update": iam.UPDATE_PERMISSION,
    "destroy": iam.DELETE_PERMISSION,
    "bulk_create": iam.CREATE_PERMISSION,
    "by_module": iam.VIEW_PERMISSION,
}

ROLE_ACTION_PERMISSIONS = {
    "list": iam.VIEW_ROLE,
    "get": iam.VIEW_ROLE,
    "create": iam.CREATE_ROLE,
    "update": iam.UPDATE_ROLE,
    "partial_update": iam.UPDATE_ROLE,
    "destroy": iam.DELETE_ROLE,
    "add_permission": iam.UPDATE_ROLE,
    "remove_permission": iam.UPDATE_ROLE,
    "assign_permissions": iam.UPDATE_ROLE,
}

USER_ACTION_PERMISSIONS = {
    "list": iam.VIEW_USER,
    "get": iam.VIEW_USER,
    "create": iam.CREATE_USER,
    "update": iam.UPDATE_USER,
    "partial_update": iam.UPDATE_USER,
    "destroy": iam.DELETE_USER,
    "change_password": iam.UPDATE_USER,
    "permissions": iam.VIEW_USER,
    "search": iam.VIEW_USER,
    "teachers": iam.VIEW_USER,
    "students": iam.VIEW_USER,
    "representatives": iam.VIEW_USER,
}
