"""
JWT Auth middleware que inyecta usuario y permisos en el request.
"""

from apps.accounts.utils import decode_token, get_user_effective_permissions


class JWTAuthMiddleware:
    """
    Middleware que procesa el token JWT en cada request.

    - Si el header Authorization: Bearer <token> está presente y es válido,
      inyecta en el request:
        request.current_user      → instancia del modelo User
        request.user_permissions  → set de codenames efectivos
        request.token_payload     → payload decodificado del JWT

    - Si no hay token o es inválido, las tres propiedades quedan en None / set vacío.
      Las vistas protegidas con @require_permission retornarán 401/403.

    Las rutas públicas (login, refresh) no requieren token.
    """

    PUBLIC_PATHS = {
        "/api/accounts/login/",
        "/api/accounts/refresh/",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.current_user = None
        request.user_permissions = set()
        request.token_payload = None

        path = request.path_info

        if path not in self.PUBLIC_PATHS:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                payload = decode_token(token)

                if payload and payload.get("type") == "access":
                    request.token_payload = payload
                    user = self._get_user(payload.get("user_id"))
                    if user and user.active:
                        request.current_user = user
                        request.user_permissions = get_user_effective_permissions(user)

        return self.get_response(request)

    @staticmethod
    def _get_user(user_id):
        if not user_id:
            return None
        try:
            from apps.accounts.models import User

            return User.objects.select_related("role").get(pk=user_id, active=True)
        except Exception:
            return None
