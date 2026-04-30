"""
Utilidades para el módulo accounts.

Incluye helpers para JWT, passwords y permisos.
"""

import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
from django.conf import settings


# ─── JWT helpers ──────────────────────────────────────────────────────────────



def _secret() -> str:
    return settings.JWT_SECRET


def generate_access_token(payload: dict) -> str:
    """
    Genera un access token JWT con expiración corta.
    payload debe contener al menos {'user_id': <int>}.
    """
    minutes = settings.JWT_ACCESS_EXPIRE_MINUTES
    data = {
        **payload,
        "type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=minutes),
        "iat": datetime.now(tz=timezone.utc),
    }
    return jwt.encode(data, _secret(), algorithm="HS256")


def generate_refresh_token(payload: dict) -> str:
    """
    Genera un refresh token JWT con expiración larga.
    payload debe contener al menos {'user_id': <int>}.
    """
    days = settings.JWT_REFRESH_EXPIRE_DAYS
    data = {
        **payload,
        "type": "refresh",
        "exp": datetime.now(tz=timezone.utc) + timedelta(days=days),
        "iat": datetime.now(tz=timezone.utc),
    }
    return jwt.encode(data, _secret(), algorithm="HS256")


def decode_token(token: str) -> dict | None:
    """
    Decodifica y valida un token JWT.
    Retorna el payload si es válido, None si expiró o es inválido.
    """
    try:
        return jwt.decode(token, _secret(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_effective_permissions(user) -> set:
    """
    Calcula el conjunto de codenames de permisos efectivos para un usuario.

    Lógica:
    1. Base: todos los permisos del rol del usuario.
    2. Overrides de UserPermission:
       - granted=True  → añade el codename (aunque no esté en el rol).
       - granted=False → quita el codename.
    """
    from apps.accounts.models import UserPermission

    effective: set = set()

    # 1. Permisos base del rol
    if user.role_id:
        role_codenames = user.role.get_all_permissions().values_list(
            "codename", flat=True
        )
        effective.update(role_codenames)

    # 2. Overrides individuales
    overrides = UserPermission.objects.filter(user=user).select_related("permission")
    for override in overrides:
        if override.granted:
            effective.add(override.permission.codename)
        else:
            effective.discard(override.permission.codename)

    return effective
