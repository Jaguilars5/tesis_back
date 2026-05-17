"""
ViewSets estándar de DRF para el módulo accounts.

Validan con los serializers y delegan al service. Cero lógica de negocio aquí.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.core.permissions import HasPermission
from apps.core.constants.permissions import accounts
from apps.core.utils import ok_response, error_response

from apps.accounts.models import Person, User, Role, Permission
from apps.accounts.services.user_service import UserService
from apps.accounts.services.role_service import RoleService
from apps.accounts.services.permission_service import PermissionService
from apps.accounts.api.serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    RoleListSerializer,
    RoleDetailSerializer,
    PermissionSerializer,
    PersonSerializer,
    UserPermissionSerializer,
    LoginSerializer,
    CustomTokenRefreshSerializer,
)
from apps.accounts.api.filters import UserFilter, RoleFilter, PermissionFilter


class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    action_permissions = {
        "list": accounts.VIEW_PERSON,
        "retrieve": accounts.VIEW_PERSON,
    }
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["names", "last_names", "document_number", "email"]
    ordering_fields = ["names", "last_names", "created_at"]
    ordering = ["last_names", "names"]


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada de login que retorna datos del usuario junto con los tokens."""

    serializer_class = LoginSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """Vista personalizada de refresh que retorna datos del usuario junto con el nuevo token."""

    serializer_class = CustomTokenRefreshSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    """
    API para gestionar permisos.

    Endpoints:
    - GET /api/accounts/permissions/ — listar
    - POST /api/accounts/permissions/ — crear
    - GET /api/accounts/permissions/{id}/ — detalle
    - PUT /api/accounts/permissions/{id}/ — actualizar
    - DELETE /api/accounts/permissions/{id}/ — eliminar
    - POST /api/accounts/permissions/search/ — buscar
    """

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    action_permissions = {
        "list": accounts.VIEW_PERMISSION,
        "retrieve": accounts.VIEW_PERMISSION,
        "create": accounts.CREATE_PERMISSION,
        "update": accounts.UPDATE_PERMISSION,
        "partial_update": accounts.UPDATE_PERMISSION,
        "destroy": accounts.DELETE_PERMISSION,
        "bulk_create": accounts.CREATE_PERMISSION,
        "by_module": accounts.VIEW_PERMISSION,
    }
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PermissionFilter
    search_fields = ["code", "description"]
    ordering_fields = ["code", "module", "created_at"]
    ordering = ["code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = PermissionService()

    def create(self, request, *args, **kwargs):
        """Crea un nuevo permiso."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            permission = self.service.create_permission(
                code=serializer.validated_data["code"],
                description=serializer.validated_data.get("description", ""),
                module=serializer.validated_data.get("module", ""),
            )
            return ok_response(self.serializer_class(permission).data, status=201)
        except ValueError as e:
            return error_response(e)

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        """Crea múltiples permisos."""
        permission_list = request.data.get("permissions", [])
        if not isinstance(permission_list, list):
            return error_response('Se espera una lista de permisos en "permissions"')

        try:
            permissions = self.service.create_permissions_bulk(permission_list)
            return ok_response(
                self.serializer_class(permissions, many=True).data, status=201
            )
        except Exception as e:
            return error_response(e)

    @action(detail=False, methods=["get"])
    def by_module(self, request):
        """Obtiene permisos por módulo."""
        module = request.query_params.get("module")
        if not module:
            return error_response('Se requiere el parámetro "module"')

        permissions = self.service.get_permissions_for_module(module)
        return ok_response(self.serializer_class(permissions, many=True).data)


class RoleViewSet(viewsets.ModelViewSet):
    """
    API para gestionar roles.

    Endpoints:
    - GET /api/accounts/roles/ — listar
    - POST /api/accounts/roles/ — crear
    - GET /api/accounts/roles/{id}/ — detalle
    - PUT /api/accounts/roles/{id}/ — actualizar
    - DELETE /api/accounts/roles/{id}/ — eliminar (soft-delete)
    - POST /api/accounts/roles/{id}/add-permission/ — agregar permiso
    - POST /api/accounts/roles/{id}/remove-permission/ — remover permiso
    """

    permission_classes = [permissions.IsAuthenticated, HasPermission]
    action_permissions = {
        "list": accounts.VIEW_ROLE,
        "retrieve": accounts.VIEW_ROLE,
        "create": accounts.CREATE_ROLE,
        "update": accounts.UPDATE_ROLE,
        "partial_update": accounts.UPDATE_ROLE,
        "destroy": accounts.DELETE_ROLE,
        "add_permission": accounts.UPDATE_ROLE,
        "remove_permission": accounts.UPDATE_ROLE,
        "assign_permissions": accounts.UPDATE_ROLE,
    }
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RoleFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = RoleService()

    def get_queryset(self):
        return Role.objects.all().prefetch_related("role_permissions__permission")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RoleDetailSerializer
        return RoleListSerializer

    def create(self, request, *args, **kwargs):
        """Crea un nuevo rol."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            role = self.service.create_role(
                name=serializer.validated_data["name"],
                description=serializer.validated_data.get("description", ""),
                active=serializer.validated_data.get("active", True),
            )
            return ok_response(RoleDetailSerializer(role).data, status=201)
        except ValueError as e:
            return error_response(e)

    @action(detail=True, methods=["post"], url_path="add-permission")
    def add_permission(self, request, pk=None):
        """Agrega un permiso a un rol."""
        permission_code = request.data.get("permission_code")
        if not permission_code:
            return error_response('Se requiere "permission_code"')

        try:
            rp, created = self.service.add_permission_to_role(pk, permission_code)
            return ok_response({"message": "Permiso agregado", "created": created})
        except ValueError as e:
            return error_response(e)

    @action(detail=True, methods=["post"], url_path="remove-permission")
    def remove_permission(self, request, pk=None):
        """Remueve un permiso de un rol."""
        permission_code = request.data.get("permission_code")
        if not permission_code:
            return error_response('Se requiere "permission_code"')

        try:
            removed = self.service.remove_permission_from_role(pk, permission_code)
            return ok_response({"message": "Permiso removido", "success": removed})
        except ValueError as e:
            return error_response(e)

    @action(detail=True, methods=["post"])
    def assign_permissions(self, request, pk=None):
        """Asigna múltiples permisos a un rol (reemplaza los existentes)."""
        permission_codes = request.data.get("permission_codes", [])
        if not isinstance(permission_codes, list):
            return error_response('Se requiere una lista en "permission_codes"')

        try:
            count = self.service.assign_permissions_to_role(pk, permission_codes)
            return ok_response({"message": f"{count} permisos asignados"})
        except ValueError as e:
            return error_response(e)


class UserViewSet(viewsets.ModelViewSet):
    """
    API para gestionar usuarios.

    Endpoints:
    - GET /api/accounts/users/ — listar
    - POST /api/accounts/users/ — crear
    - GET /api/accounts/users/{id}/ — detalle
    - PUT /api/accounts/users/{id}/ — actualizar
    - DELETE /api/accounts/users/{id}/ — desactivar (soft-delete)
    - POST /api/accounts/users/{id}/change-password/ — cambiar contraseña
    - POST /api/accounts/users/{id}/grant-permission/ — otorgar permiso
    - POST /api/accounts/users/{id}/revoke-permission/ — revocar permiso
    - GET /api/accounts/users/{id}/permissions/ — ver permisos
    """

    permission_classes = [permissions.IsAuthenticated, HasPermission]
    action_permissions = {
        "list": accounts.VIEW_USER,
        "retrieve": accounts.VIEW_USER,
        "create": accounts.CREATE_USER,
        "update": accounts.UPDATE_USER,
        "partial_update": accounts.UPDATE_USER,
        "destroy": accounts.DELETE_USER,
        "change_password": accounts.UPDATE_USER,
        "grant_permission": accounts.UPDATE_USER,
        "revoke_permission": accounts.UPDATE_USER,
        "permissions": accounts.VIEW_USER,
        "search": accounts.VIEW_USER,
    }
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = [
        "person__names",
        "person__last_names",
        "email",
        "person__document_number",
    ]
    ordering_fields = ["email", "created_at"]
    ordering = ["email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = UserService()

    def get_queryset(self):
        return User.objects.select_related("institution")

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "retrieve":
            return UserDetailSerializer
        return UserListSerializer

    def create(self, request, *args, **kwargs):
        """Crea un nuevo usuario."""
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = self.service.create_user(
                document_number=serializer.validated_data["document_number"],
                names=serializer.validated_data["names"],
                last_names=serializer.validated_data["last_names"],
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                role_id=serializer.validated_data["role_id"],
                institution_id=serializer.validated_data["institution_id"],
            )
            return ok_response(UserDetailSerializer(user).data, status=201)
        except ValueError as e:
            return error_response(e)

    @action(detail=True, methods=["post"], url_path="change-password")
    def change_password(self, request, pk=None):
        """Cambia la contraseña de un usuario."""
        new_password = request.data.get("new_password")
        if not new_password:
            return error_response('Se requiere "new_password"')

        try:
            user = self.service.change_password(pk, new_password)
            return ok_response({"message": "Contraseña actualizada"})
        except ValueError as e:
            return error_response(e)

    @action(detail=True, methods=["post"], url_path="grant-permission")
    def grant_permission(self, request, pk=None):
        """Otorga un permiso específico a un usuario."""
        permission_code = request.data.get("permission_code")
        reason = request.data.get("reason", "")

        if not permission_code:
            return error_response('Se requiere "permission_code"')

        try:
            up = self.service.grant_permission(
                pk, permission_code, reason, request.user.id
            )
            return ok_response(UserPermissionSerializer(up).data)
        except ValueError as e:
            return error_response(e)

    @action(detail=True, methods=["post"], url_path="revoke-permission")
    def revoke_permission(self, request, pk=None):
        """Revoca un permiso específico a un usuario."""
        permission_code = request.data.get("permission_code")
        reason = request.data.get("reason", "")

        if not permission_code:
            return error_response('Se requiere "permission_code"')

        try:
            up = self.service.revoke_permission(
                pk, permission_code, reason, request.user.id
            )
            return ok_response(UserPermissionSerializer(up).data)
        except ValueError as e:
            return error_response(e)

    @action(detail=True, methods=["get"])
    def permissions(self, request, pk=None):
        """Obtiene todos los permisos de un usuario."""
        try:
            permissions = self.service.get_user_permissions(pk)
            return ok_response({"permissions": list(permissions)})
        except Exception as e:
            return error_response(e)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Búsqueda personalizada de usuarios."""
        query = request.query_params.get("q")
        institution_id = request.query_params.get("institution_id")

        if not query:
            return error_response('Se requiere el parámetro "q"')

        users = self.service.search_users(query, institution_id)
        serializer = UserListSerializer(users, many=True)
        return ok_response(serializer.data)
