"""
Decoradores para el módulo accounts.

Incluye decoradores para proteger vistas con permisos.
"""

from functools import wraps
from rest_framework.response import Response


def require_permission(codename: str):
    """
    Decorador para proteger vistas con un permiso específico.

    Uso:
        @api_view(['POST'])
        @require_permission('users.user_list')
        def user_list(request):
            ...

    Retorna:
        401  si no hay usuario autenticado en el request (token ausente o inválido).
        403  si el usuario está autenticado pero no tiene el permiso requerido.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.current_user is None:
                return Response(
                    {
                        "ok": False,
                        "data": {},
                        "msg": "Authentication required. Provide a valid Bearer token.",
                    },
                    status=401,
                )
            if codename not in request.user_permissions:
                return Response(
                    {
                        "ok": False,
                        "data": {},
                        "msg": f"Forbidden. Missing permission: {codename}",
                    },
                    status=403,
                )
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
