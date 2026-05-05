from functools import wraps

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class HasPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        action = getattr(view, "action", None)
        if action is None:
            action = getattr(view, "action_map", {}).get(request.method.lower(), None)

        action_permissions = getattr(view, "action_permissions", None)
        if action_permissions is None:
            return False

        codename = action_permissions.get(action)
        if codename is None:
            return False

        return request.user.has_perm(codename)


def require_permission(codename):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied(
                    "No tienes permiso para realizar esta acci\u00f3n."
                )
            if not request.user.has_perm(codename):
                raise PermissionDenied(
                    "No tienes permiso para realizar esta acci\u00f3n."
                )
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
