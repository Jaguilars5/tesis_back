"""
URLs para el API del módulo accounts.

Registra los ViewSets en un router DRF.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from apps.accounts.api.views import PermissionViewSet, PersonViewSet, RoleViewSet, UserViewSet, CustomTokenObtainPairView, CustomTokenRefreshView

router = DefaultRouter()
router.register(r"permissions", PermissionViewSet, basename="permission")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"users", UserViewSet, basename="user")
router.register(r"persons", PersonViewSet, basename="person")

urlpatterns = [
    path("", include(router.urls)),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]
