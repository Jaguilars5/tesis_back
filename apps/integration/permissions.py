from apps.core.constants.permissions import integration as perm

ACTION_PERMISSIONS = {
    "list": perm.VIEW_SYNC_QUEUE,
    "retrieve": perm.VIEW_SYNC_QUEUE,
    "create": perm.CREATE_SYNC_QUEUE,
    "update": perm.UPDATE_SYNC_QUEUE,
    "partial_update": perm.UPDATE_SYNC_QUEUE,
    "destroy": perm.DELETE_SYNC_QUEUE,
}
