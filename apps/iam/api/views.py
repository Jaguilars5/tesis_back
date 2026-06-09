from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.core.api.permissions import HasPermission
from apps.core.constants.permissions import iam

from apps.iam.repositories import PermissionRepository, RoleRepository, UserRepository
from apps.iam.services.user_service import UserService
from apps.iam.services.role_service import RoleService
from apps.iam.services.permission_service import PermissionService
from apps.iam.api.serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    RoleListSerializer,
    RoleDetailSerializer,
    PermissionSerializer,
    LoginSerializer,
    LoginResponseSerializer,
    TokenRefreshResponseSerializer,
    CustomTokenRefreshSerializer,
)
from apps.iam.api.filters import UserFilter, RoleFilter, PermissionFilter


@extend_schema(
    tags=["iam"],
    summary="Iniciar sesión",
    description="Autentica un usuario con username y contraseña. Retorna tokens JWT y datos del usuario.",
    request=LoginSerializer,
    responses={200: LoginResponseSerializer},
)
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = LoginSerializer


@extend_schema(
    tags=["iam"],
    summary="Refrescar token",
    description="Refresca el token de acceso usando un refresh token válido.",
    request=CustomTokenRefreshSerializer,
    responses={200: TokenRefreshResponseSerializer},
)
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = CustomTokenRefreshSerializer


@extend_schema_view(
    list=extend_schema(summary="Listar permisos", tags=["iam"]),
    retrieve=extend_schema(summary="Obtener permiso", tags=["iam"]),
    create=extend_schema(summary="Crear permiso", tags=["iam"]),
    update=extend_schema(summary="Actualizar permiso", tags=["iam"]),
    partial_update=extend_schema(
        summary="Actualizar permiso parcialmente", tags=["iam"]
    ),
    destroy=extend_schema(summary="Eliminar permiso", tags=["iam"]),
    bulk_create=extend_schema(summary="Crear múltiples permisos", tags=["iam"]),
    by_module=extend_schema(summary="Permisos por módulo", tags=["iam"]),
)
class PermissionViewSet(viewsets.ModelViewSet):
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    action_permissions = {
        "list": iam.VIEW_PERMISSION,
        "retrieve": iam.VIEW_PERMISSION,
        "create": iam.CREATE_PERMISSION,
        "update": iam.UPDATE_PERMISSION,
        "partial_update": iam.UPDATE_PERMISSION,
        "destroy": iam.DELETE_PERMISSION,
        "bulk_create": iam.CREATE_PERMISSION,
        "by_module": iam.VIEW_PERMISSION,
    }
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PermissionFilter
    search_fields = ["code", "description"]
    ordering_fields = ["code", "module", "created_at"]
    ordering = ["code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = PermissionService()

    def get_queryset(self):
        return PermissionRepository.get_all()

    def create(self, request, *args, **kwargs):
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
        module = request.query_params.get("module")
        if not module:
            return Response('Se requiere el parámetro "module"', status=400)

        permissions = self.service.get_permissions_for_module(module)
        return Response(self.serializer_class(permissions, many=True).data)


@extend_schema_view(
    list=extend_schema(summary="Listar roles", tags=["iam"]),
    retrieve=extend_schema(summary="Obtener rol", tags=["iam"]),
    create=extend_schema(summary="Crear rol", tags=["iam"]),
    update=extend_schema(summary="Actualizar rol", tags=["iam"]),
    partial_update=extend_schema(
        summary="Actualizar rol parcialmente", tags=["iam"]
    ),
    destroy=extend_schema(summary="Eliminar rol", tags=["iam"]),
    add_permission=extend_schema(summary="Agregar permiso a rol", tags=["iam"]),
    remove_permission=extend_schema(
        summary="Remover permiso de rol", tags=["iam"]
    ),
    assign_permissions=extend_schema(
        summary="Asignar permisos a rol", tags=["iam"]
    ),
)
class RoleViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    action_permissions = {
        "list": iam.VIEW_ROLE,
        "retrieve": iam.VIEW_ROLE,
        "create": iam.CREATE_ROLE,
        "update": iam.UPDATE_ROLE,
        "partial_update": iam.UPDATE_ROLE,
        "destroy": iam.DELETE_ROLE,
        "add_permission": iam.UPDATE_ROLE,
        "remove_permission": iam.UPDATE_ROLE,
        "assign_permissions": iam.UPDATE_ROLE,
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
        return RoleRepository.get_all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RoleDetailSerializer
        return RoleListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            role = self.service.create_role(
                name=serializer.validated_data["name"],
                description=serializer.validated_data.get("description", ""),
                active=serializer.validated_data.get("is_active", True),
            )
            return Response(RoleDetailSerializer(role).data, status=201)
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=True, methods=["post"], url_path="add-permission")
    def add_permission(self, request, pk=None):
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
        permission_codes = request.data.get("permission_codes", [])
        if not isinstance(permission_codes, list):
            return Response('Se requiere una lista en "permission_codes"', status=400)

        try:
            count = self.service.assign_permissions_to_role(pk, permission_codes)
            return Response({"message": f"{count} permisos asignados"})
        except ValueError as e:
            return Response(str(e), status=400)


@extend_schema_view(
    list=extend_schema(summary="Listar usuarios", tags=["iam"]),
    retrieve=extend_schema(summary="Obtener usuario", tags=["iam"]),
    create=extend_schema(summary="Crear usuario", tags=["iam"]),
    update=extend_schema(summary="Actualizar usuario", tags=["iam"]),
    partial_update=extend_schema(
        summary="Actualizar usuario parcialmente", tags=["iam"]
    ),
    destroy=extend_schema(summary="Desactivar usuario", tags=["iam"]),
    change_password=extend_schema(summary="Cambiar contraseña", tags=["iam"]),
    permissions=extend_schema(summary="Permisos del usuario", tags=["iam"]),
    search=extend_schema(summary="Buscar usuarios", tags=["iam"]),
)
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, HasPermission]
    action_permissions = {
        "list": iam.VIEW_USER,
        "retrieve": iam.VIEW_USER,
        "create": iam.CREATE_USER,
        "update": iam.UPDATE_USER,
        "partial_update": iam.UPDATE_USER,
        "destroy": iam.DELETE_USER,
        "change_password": iam.UPDATE_USER,
        "permissions": iam.VIEW_USER,
        "search": iam.VIEW_USER,
    }
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = [
        "username",
        "person__names",
        "person__last_names",
        "email",
        "person__document_number",
    ]
    ordering_fields = ["username", "email", "created_at"]
    ordering = ["username"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = UserService()

    def get_queryset(self):
        return UserRepository.get_all_active()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "retrieve":
            return UserDetailSerializer
        return UserListSerializer

    def create(self, request, *args, **kwargs):
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
        try:
            permissions = self.service.get_user_permissions(pk)
            return Response({"permissions": list(permissions)})
        except Exception as e:
            return Response(str(e), status=400)

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q")

        if not query:
            return Response('Se requiere el parámetro "q"', status=400)

        users = self.service.search_users(query)
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)
