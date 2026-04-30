"""
Middleware para el módulo accounts.

Incluye JWT Auth middleware que inyecta usuario y permisos en el request.
"""

from .jwt_auth import JWTAuthMiddleware

__all__ = ["JWTAuthMiddleware"]
