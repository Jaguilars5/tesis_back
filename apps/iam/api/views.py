from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.core.api.mixins import SoftDeleteModelMixin
from apps.core.api.permissions import HasPermission
from apps.core.constants.permissions import iam
from apps.core.notifications.mail import (
    send_notification_email,
    send_password_reset_email,
)
from apps.core.utils import ok_response, error_response

from apps.iam.domain.services import UserService, RoleService, PermissionService
from apps.iam.application.serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    RoleListSerializer,
    RoleDetailSerializer,
    PermissionSerializer,
    LoginSerializer,
    LoginResponseSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    TokenRefreshResponseSerializer,
    CustomTokenRefreshSerializer,
)
from apps.iam.api.filters import UserFilter, RoleFilter, PermissionFilter
from apps.iam.permissions import (
    PERMISSION_ACTION_PERMISSIONS,
    ROLE_ACTION_PERMISSIONS,
    USER_ACTION_PERMISSIONS,
)
from .base import BaseIamViewSet


def send_mail(subject, message, from_email, recipient_list, fail_silently=False):
    sent = 0
    reset_url = next(
        (line.strip() for line in message.splitlines() if "/reset-password/" in line),
        "",
    )
    for recipient in recipient_list:
        delivered = (
            send_password_reset_email(recipient, reset_url)
            if reset_url
            else send_notification_email(recipient, subject, message)
        )
        if delivered:
            sent += 1
    if not fail_silently and sent < len(recipient_list):
        raise RuntimeError("No se pudo enviar el correo")
    return sent


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


PASSWORD_RESET_SENT_MSG = "Si los datos coinciden con una cuenta activa, enviaremos instrucciones al correo registrado."


@extend_schema(
    tags=["iam"],
    summary="Solicitar recuperacion de contraseña",
    description="Genera un enlace de recuperacion para el usuario o correo indicado.",
    request=PasswordResetRequestSerializer,
)
class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data["identifier"].strip()
        user = UserService.get_user_for_password_reset(identifier)

        if user and user.person and user.person.email:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            frontend_base_url = getattr(
                settings,
                "PASSWORD_RESET_FRONTEND_URL",
                request.headers.get("Origin") or "http://localhost:5173",
            ).rstrip("/")
            reset_url = f"{frontend_base_url}/reset-password/{uid}/{token}"
            send_mail(
                subject="Recuperacion de contraseña",
                message=(
                    "Recibimos una solicitud para restablecer tu contraseña.\n\n"
                    f"Ingresa al siguiente enlace para crear una nueva contraseña:\n{reset_url}\n\n"
                    "Si no solicitaste este cambio, puedes ignorar este mensaje."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.person.email],
                fail_silently=False,
            )

        return ok_response(msg=PASSWORD_RESET_SENT_MSG)


@extend_schema(
    tags=["iam"],
    summary="Confirmar recuperacion de contraseña",
    description="Valida el token de recuperacion y actualiza la contraseña.",
    request=PasswordResetConfirmSerializer,
)
class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user_id = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
            user = UserService.get_user(user_id)
        except (TypeError, ValueError, OverflowError, DjangoValidationError):
            return error_response(
                "El enlace de recuperacion no es valido o ha expirado.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        token = serializer.validated_data["token"]
        if not default_token_generator.check_token(user, token):
            return error_response(
                "El enlace de recuperacion no es valido o ha expirado.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        new_password = serializer.validated_data["new_password"]
        try:
            validate_password(new_password, user=user)
            UserService.change_password(user.id, new_password)
        except DjangoValidationError as e:
            return error_response(
                "La contraseña no cumple los requisitos.",
                data={"password_errors": list(e.messages)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return ok_response(msg="Contraseña actualizada correctamente.")


@extend_schema_view(
    list=extend_schema(summary="Listar permisos", tags=["iam"]),
    get=extend_schema(summary="Obtener permiso", tags=["iam"]),
    create=extend_schema(summary="Crear permiso", tags=["iam"]),
    update=extend_schema(summary="Actualizar permiso", tags=["iam"]),
    partial_update=extend_schema(
        summary="Actualizar permiso parcialmente", tags=["iam"]
    ),
    destroy=extend_schema(summary="Eliminar permiso", tags=["iam"]),
    bulk_create=extend_schema(summary="Crear múltiples permisos", tags=["iam"]),
    by_module=extend_schema(summary="Permisos por módulo", tags=["iam"]),
)
class PermissionViewSet(SoftDeleteModelMixin, BaseIamViewSet):
    serializer_class = PermissionSerializer
    action_permissions = PERMISSION_ACTION_PERMISSIONS
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PermissionFilter
    search_fields = ["code", "description"]
    ordering_fields = ["code", "module", "created_at"]
    ordering = ["code"]
    service = PermissionService

    def get_queryset(self):
        return self.service.list_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            permission = self.service.create_permission(
                code=serializer.validated_data["code"],
                description=serializer.validated_data.get("description", ""),
                module=serializer.validated_data.get("module", ""),
            )
            return ok_response(
                self.serializer_class(permission).data,
                msg="Permiso creado exitosamente",
                status_code=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        permission_list = request.data.get("permissions", [])
        if not isinstance(permission_list, list):
            return error_response(
                'Se espera una lista de permisos en "permissions"',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            permissions = self.service.create_permissions_bulk(permission_list)
            return ok_response(
                self.serializer_class(permissions, many=True).data,
                msg="Permisos creados exitosamente",
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="by-module")
    def by_module(self, request):
        module = request.query_params.get("module")
        if not module:
            return error_response(
                'Se requiere el parámetro "module"',
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        permissions = self.service.get_permissions_for_module(module)
        return ok_response(self.serializer_class(permissions, many=True).data)


@extend_schema_view(
    list=extend_schema(summary="Listar roles", tags=["iam"]),
    get=extend_schema(summary="Obtener rol", tags=["iam"]),
    create=extend_schema(summary="Crear rol", tags=["iam"]),
    update=extend_schema(summary="Actualizar rol", tags=["iam"]),
    partial_update=extend_schema(summary="Actualizar rol parcialmente", tags=["iam"]),
    destroy=extend_schema(summary="Eliminar rol", tags=["iam"]),
    add_permission=extend_schema(summary="Agregar permiso a rol", tags=["iam"]),
    remove_permission=extend_schema(summary="Remover permiso de rol", tags=["iam"]),
    assign_permissions=extend_schema(summary="Asignar permisos a rol", tags=["iam"]),
    soft_delete=extend_schema(summary="Desactivar rol con cascada", tags=["iam"]),
)
class RoleViewSet(SoftDeleteModelMixin, BaseIamViewSet):
    action_permissions = ROLE_ACTION_PERMISSIONS
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RoleFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    service = RoleService

    def get_queryset(self):
        return self.service.list_roles()

    def get_serializer_class(self):
        if self.action == "get":
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
            return ok_response(
                RoleDetailSerializer(role).data,
                msg="Rol creado exitosamente",
                status_code=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="add-permission")
    def add_permission(self, request, pk=None):
        permission_code = request.data.get("permission_code")
        if not permission_code:
            return error_response(
                'Se requiere "permission_code"',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            rp, created = self.service.add_permission_to_role(pk, permission_code)
            return ok_response({"message": "Permiso agregado", "created": created})
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="remove-permission")
    def remove_permission(self, request, pk=None):
        permission_code = request.data.get("permission_code")
        if not permission_code:
            return error_response(
                'Se requiere "permission_code"',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            removed = self.service.remove_permission_from_role(pk, permission_code)
            return ok_response({"message": "Permiso removido", "success": removed})
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def assign_permissions(self, request, pk=None):
        permission_codes = request.data.get("permission_codes", [])
        if not isinstance(permission_codes, list):
            return error_response(
                'Se requiere una lista en "permission_codes"',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            count = self.service.assign_permissions_to_role(pk, permission_codes)
            return ok_response({"message": f"{count} permisos asignados"})
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(summary="Listar usuarios", tags=["iam"]),
    get=extend_schema(summary="Obtener usuario", tags=["iam"]),
    create=extend_schema(summary="Crear usuario", tags=["iam"]),
    update=extend_schema(summary="Actualizar usuario", tags=["iam"]),
    partial_update=extend_schema(
        summary="Actualizar usuario parcialmente", tags=["iam"]
    ),
    destroy=extend_schema(summary="Desactivar usuario", tags=["iam"]),
    change_password=extend_schema(summary="Cambiar contraseña", tags=["iam"]),
    permissions=extend_schema(summary="Permisos del usuario", tags=["iam"]),
    search=extend_schema(summary="Buscar usuarios", tags=["iam"]),
    teachers=extend_schema(summary="Listar usuarios con rol docente", tags=["iam"]),
    students=extend_schema(summary="Listar usuarios con rol estudiante", tags=["iam"]),
    representatives=extend_schema(
        summary="Listar usuarios con rol representante", tags=["iam"]
    ),
)
class UserViewSet(SoftDeleteModelMixin, BaseIamViewSet):
    """
    ViewSet para gestión de usuarios.
    DELETE realiza desactivación lógica (is_active=False).
    """

    action_permissions = USER_ACTION_PERMISSIONS
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = [
        "username",
        "person__names",
        "person__last_names",
        "person__email",
        "person__document_number",
    ]
    ordering_fields = ["username", "person__email", "created_at"]
    ordering = ["username"]
    service = UserService

    def destroy(self, request, *args, **kwargs):
        """
        Desactiva un usuario en lugar de borrarlo físicamente.
        Alineado con la documentación: 'Desactivar usuario'.
        """
        try:
            user = self.service.deactivate_user(kwargs.get("pk"))
            return ok_response(
                {"id": user.id, "is_active": user.is_active},
                msg="Usuario desactivado exitosamente",
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return self.service.list_users()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ("get", "update", "partial_update"):
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
                birth_date=serializer.validated_data.get("birth_date"),
                phone=serializer.validated_data.get("phone", ""),
                document_type_id=serializer.validated_data.get("document_type"),
                parish_id=serializer.validated_data.get("parish"),
            )
            return ok_response(
                UserDetailSerializer(user).data,
                msg="Usuario creado exitosamente",
                status_code=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="change-password")
    def change_password(self, request, pk=None):
        new_password = request.data.get("new_password")
        if not new_password:
            return error_response(
                'Se requiere "new_password"',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = self.service.change_password(pk, new_password)
            return ok_response(
                {
                    "message": "Contraseña actualizada",
                    "must_change_password": user.must_change_password,
                }
            )
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)
        except DjangoValidationError as e:
            return error_response(
                {"password_errors": list(e.messages)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["get"])
    def permissions(self, request, pk=None):
        try:
            permissions = self.service.get_user_permissions(pk)
            return ok_response({"permissions": list(permissions)})
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q")
        if not query:
            return error_response(
                'Se requiere el parámetro "q"',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        users = self.service.search_users(query)
        serializer = UserListSerializer(users, many=True)
        return ok_response(serializer.data)

    @action(detail=False, methods=["get"])
    def teachers(self, request):
        users = self.service.list_users_by_role_code("DOCENTE")
        serializer = UserListSerializer(users, many=True)
        return ok_response(serializer.data)

    @action(detail=False, methods=["get"])
    def students(self, request):
        users = self.service.list_users_by_role_code("ESTUDIANTE")
        serializer = UserListSerializer(users, many=True)
        return ok_response(serializer.data)

    @action(detail=False, methods=["get"])
    def representatives(self, request):
        search = request.query_params.get("search", "")
        users = self.service.search_users_by_role_code("REPRESENTANTE", search=search)
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = UserListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserListSerializer(users, many=True)
        return ok_response(serializer.data)
