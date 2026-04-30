"""
URLs para el API del módulo accounts.

Registra los ViewSets en un router DRF.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.accounts.api.views import PermissionViewSet, RoleViewSet, UserViewSet

router = DefaultRouter()
router.register(r"permissions", PermissionViewSet, basename="permission")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
