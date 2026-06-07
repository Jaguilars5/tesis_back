"""
ViewSets estándar de DRF para el módulo accounts.

Validan con los serializers y delegan al service. Cero lógica de negocio aquí.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.core.api.permissions import HasPermission
from apps.core.constants.permissions import accounts

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
    LoginSerializer,
    LoginResponseSerializer,
    TokenRefreshResponseSerializer,
    CustomTokenRefreshSerializer,
)
from apps.accounts.api.filters import UserFilter, RoleFilter, PermissionFilter


@extend_schema_view(
    list=extend_schema(summary="Listar personas", tags=["accounts"]),
    retrieve=extend_schema(summary="Obtener persona", tags=["accounts"]),
)
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


@extend_schema(
    tags=["accounts"],
    summary="Iniciar sesión",
    description="Autentica un usuario con email y contraseña. Retorna tokens JWT y datos del usuario.",
    request=LoginSerializer,
    responses={200: LoginResponseSerializer},
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada de login que retorna datos del usuario junto con los tokens."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = LoginSerializer


@extend_schema(
    tags=["accounts"],
    summary="Refrescar token",
    description="Refresca el token de acceso usando un refresh token válido.",
    request=CustomTokenRefreshSerializer,
    responses={200: TokenRefreshResponseSerializer},
)
class CustomTokenRefreshView(TokenRefreshView):
    """Vista personalizada de refresh que retorna datos del usuario junto con el nuevo token."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = CustomTokenRefreshSerializer


@extend_schema_view(
    list=extend_schema(summary="Listar permisos", tags=["accounts"]),
    retrieve=extend_schema(summary="Obtener permiso", tags=["accounts"]),
    create=extend_schema(summary="Crear permiso", tags=["accounts"]),
    update=extend_schema(summary="Actualizar permiso", tags=["accounts"]),
    partial_update=extend_schema(
        summary="Actualizar permiso parcialmente", tags=["accounts"]
    ),
    destroy=extend_schema(summary="Eliminar permiso", tags=["accounts"]),
    bulk_create=extend_schema(summary="Crear múltiples permisos", tags=["accounts"]),
    by_module=extend_schema(summary="Permisos por módulo", tags=["accounts"]),
)
class PermissionViewSet(viewsets.ModelViewSet):
    """
    API para gestionar permisos.
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
            return Response(self.serializer_class(permission).data, status=201)
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        """Crea múltiples permisos."""
        permission_list = request.data.get("permissions", [])
        if not isinstance(permission_list, list):
            return Response(
                'Se espera una lista de permisos en "permissions"', status=400
            )

        try:
            permissions = self.service.create_permissions_bulk(permission_list)
            return Response(
                self.serializer_class(permissions, many=True).data, status=201
            )
        except Exception as e:
            return Response(str(e), status=400)

    @action(detail=False, methods=["get"])
    def by_module(self, request):
        """Obtiene permisos por módulo."""
        module = request.query_params.get("module")
        if not module:
            return Response('Se requiere el parámetro "module"', status=400)

        permissions = self.service.get_permissions_for_module(module)
        return Response(self.serializer_class(permissions, many=True).data)


@extend_schema_view(
    list=extend_schema(summary="Listar roles", tags=["accounts"]),
    retrieve=extend_schema(summary="Obtener rol", tags=["accounts"]),
    create=extend_schema(summary="Crear rol", tags=["accounts"]),
    update=extend_schema(summary="Actualizar rol", tags=["accounts"]),
    partial_update=extend_schema(
        summary="Actualizar rol parcialmente", tags=["accounts"]
    ),
    destroy=extend_schema(summary="Eliminar rol", tags=["accounts"]),
    add_permission=extend_schema(summary="Agregar permiso a rol", tags=["accounts"]),
    remove_permission=extend_schema(
        summary="Remover permiso de rol", tags=["accounts"]
    ),
    assign_permissions=extend_schema(
        summary="Asignar permisos a rol", tags=["accounts"]
    ),
)
class RoleViewSet(viewsets.ModelViewSet):
    """
    API para gestionar roles.
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
            return Response(RoleDetailSerializer(role).data, status=201)
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=True, methods=["post"], url_path="add-permission")
    def add_permission(self, request, pk=None):
        """Agrega un permiso a un rol."""
        permission_code = request.data.get("permission_code")
        if not permission_code:
            return Response('Se requiere "permission_code"', status=400)

        try:
            rp, created = self.service.add_permission_to_role(pk, permission_code)
            return Response({"message": "Permiso agregado", "created": created})
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=True, methods=["post"], url_path="remove-permission")
    def remove_permission(self, request, pk=None):
        """Remueve un permiso de un rol."""
        permission_code = request.data.get("permission_code")
        if not permission_code:
            return Response('Se requiere "permission_code"', status=400)

        try:
            removed = self.service.remove_permission_from_role(pk, permission_code)
            return Response({"message": "Permiso removido", "success": removed})
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=True, methods=["post"])
    def assign_permissions(self, request, pk=None):
        """Asigna múltiples permisos a un rol (reemplaza los existentes)."""
        permission_codes = request.data.get("permission_codes", [])
        if not isinstance(permission_codes, list):
            return Response('Se requiere una lista en "permission_codes"', status=400)

        try:
            count = self.service.assign_permissions_to_role(pk, permission_codes)
            return Response({"message": f"{count} permisos asignados"})
        except ValueError as e:
            return Response(str(e), status=400)


@extend_schema_view(
    list=extend_schema(summary="Listar usuarios", tags=["accounts"]),
    retrieve=extend_schema(summary="Obtener usuario", tags=["accounts"]),
    create=extend_schema(summary="Crear usuario", tags=["accounts"]),
    update=extend_schema(summary="Actualizar usuario", tags=["accounts"]),
    partial_update=extend_schema(
        summary="Actualizar usuario parcialmente", tags=["accounts"]
    ),
    destroy=extend_schema(summary="Desactivar usuario", tags=["accounts"]),
    change_password=extend_schema(summary="Cambiar contraseña", tags=["accounts"]),
    permissions=extend_schema(summary="Permisos del usuario", tags=["accounts"]),
    search=extend_schema(summary="Buscar usuarios", tags=["accounts"]),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    API para gestionar usuarios.
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
        return User.objects.all()

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
            )
            return Response(UserDetailSerializer(user).data, status=201)
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=True, methods=["post"], url_path="change-password")
    def change_password(self, request, pk=None):
        """Cambia la contraseña de un usuario."""
        new_password = request.data.get("new_password")
        if not new_password:
            return Response('Se requiere "new_password"', status=400)

        try:
            user = self.service.change_password(pk, new_password)
            return Response({"message": "Contraseña actualizada"})
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=True, methods=["get"])
    def permissions(self, request, pk=None):
        """Obtiene todos los permisos de un usuario."""
        try:
            permissions = self.service.get_user_permissions(pk)
            return Response({"permissions": list(permissions)})
        except Exception as e:
            return Response(str(e), status=400)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Búsqueda personalizada de usuarios."""
        query = request.query_params.get("q")
        institution_id = request.query_params.get("institution_id")

        if not query:
            return Response('Se requiere el parámetro "q"', status=400)

        users = self.service.search_users(query)
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)
