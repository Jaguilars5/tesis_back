"""
Tests de integración adicionales para el módulo accounts.

Cubre brechas detectadas:
1. Pruebas de control de acceso RBAC negativas y positivas para endpoints protegidos.
2. Pruebas del CustomTokenRefreshView (/api/accounts/refresh/) y CustomTokenObtainPairView.
3. Pruebas para PersonViewSet (/api/accounts/persons/).
4. Pruebas de filtros avanzados (UserFilter, RoleFilter, PermissionFilter).
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Person, User, Role, Permission, UserRole, RolePermission
from apps.core.tests.helpers import create_test_user
from apps.core.constants.permissions import accounts


class SecurityAndRBACAPITest(TestCase):
    """Tests para control de accesos basados en roles y permisos (RBAC)."""

    def setUp(self):
        self.client = APIClient()

        # Crear permisos necesarios
        self.view_users_perm = Permission.objects.create(
            code=accounts.VIEW_USER, module="accounts", description="Ver usuarios"
        )
        self.create_users_perm = Permission.objects.create(
            code=accounts.CREATE_USER, module="accounts", description="Crear usuarios"
        )
        self.view_roles_perm = Permission.objects.create(
            code=accounts.VIEW_ROLE, module="accounts", description="Ver roles"
        )

        # Crear rol limitado
        self.limited_role = Role.objects.create(
            name="Limited Role", code="LIMITED", description="Rol con accesos limitados"
        )
        # Asignar solo permiso de lectura a ese rol
        RolePermission.objects.create(role=self.limited_role, permission=self.view_users_perm)

        # Crear usuario con rol limitado (no superusuario)
        self.limited_user = create_test_user(
            email="limited@example.com",
            dni="DNI-LIMITED",
            names="Limited",
            last_names="User",
            is_superuser=False,
        )
        UserRole.objects.create(user=self.limited_user, role=self.limited_role)

        # Crear usuario sin ningún rol ni permisos
        self.no_permission_user = create_test_user(
            email="noperms@example.com",
            dni="DNI-NOPERMS",
            names="No",
            last_names="Perms",
            is_superuser=False,
        )

    def test_get_users_with_proper_permission(self):
        """Usuario con permiso view_user puede listar usuarios."""
        self.client.force_authenticate(user=self.limited_user)
        response = self.client.get("/api/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])

    def test_get_users_without_permission_forbidden(self):
        """Usuario sin permiso view_user recibe 403 Forbidden al listar usuarios."""
        self.client.force_authenticate(user=self.no_permission_user)
        response = self.client.get("/api/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["ok"])

    def test_create_user_without_permission_forbidden(self):
        """Usuario sin create_user recibe 403 Forbidden al intentar crear usuario."""
        self.client.force_authenticate(user=self.limited_user)
        data = {
            "document_number": "999888777",
            "names": "Nuevo",
            "last_names": "Usuario",
            "email": "nuevo@example.com",
            "password": "securepassword123",
            "role_id": self.limited_role.id,
        }
        response = self.client.post("/api/accounts/users/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_after_granting_permission(self):
        """Al agregar el permiso al rol, el usuario limitado puede crear un usuario."""
        # Agregar permiso de creación al rol
        RolePermission.objects.create(role=self.limited_role, permission=self.create_users_perm)

        self.client.force_authenticate(user=self.limited_user)
        data = {
            "document_number": "999888777",
            "names": "Nuevo",
            "last_names": "Usuario",
            "email": "nuevo@example.com",
            "password": "securepassword123",
            "role_id": self.limited_role.id,
        }
        response = self.client.post("/api/accounts/users/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])


class TokenRefreshAndJWTAPITest(TestCase):
    """Tests para CustomTokenRefreshView y obtención de token personalizado."""

    def setUp(self):
        self.client = APIClient()
        self.role = Role.objects.create(name="Docente", code="DOCENTE")
        self.view_users_perm = Permission.objects.create(
            code=accounts.VIEW_USER, module="accounts"
        )
        RolePermission.objects.create(role=self.role, permission=self.view_users_perm)

        self.user = create_test_user(
            email="docente@example.com",
            dni="DNI-DOCENTE",
            names="Docente",
            last_names="Prueba",
            is_superuser=False,
            password="testpassword123",
        )
        UserRole.objects.create(user=self.user, role=self.role)

    def test_login_returns_custom_payload(self):
        """Verifica que el login retorne los metadatos completos y permisos del usuario."""
        data = {
            "email": "docente@example.com",
            "password": "testpassword123",
        }
        response = self.client.post("/api/accounts/login/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user_data = response.data["user"]
        self.assertEqual(user_data["email"], "docente@example.com")
        self.assertEqual(user_data["dni"], "DNI-DOCENTE")
        self.assertEqual(user_data["role"], "Docente")
        self.assertEqual(user_data["role_id"], self.role.id)
        self.assertIn("accounts.view_user", user_data["permissions"])

    def test_refresh_token_returns_custom_payload(self):
        """Verifica que la renovación de token (refresh) incluya el perfil extendido del usuario."""
        refresh = RefreshToken.for_user(self.user)
        data = {
            "refresh": str(refresh),
        }
        response = self.client.post("/api/accounts/refresh/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        
        user_data = response.data["user"]
        self.assertEqual(user_data["email"], "docente@example.com")
        self.assertEqual(user_data["dni"], "DNI-DOCENTE")
        self.assertEqual(user_data["role"], "Docente")
        self.assertIn("accounts.view_user", user_data["permissions"])


class PersonAPITest(TestCase):
    """Tests para los endpoints de Person (ReadOnlyModelViewSet)."""

    def setUp(self):
        self.client = APIClient()
        self.view_person_perm = Permission.objects.create(
            code=accounts.VIEW_PERSON, module="accounts"
        )
        self.role = Role.objects.create(name="Docente", code="DOCENTE")
        RolePermission.objects.create(role=self.role, permission=self.view_person_perm)

        self.user = create_test_user(
            email="docente@example.com",
            dni="DNI-DOCENTE",
            names="Docente",
            last_names="Prueba",
        )
        UserRole.objects.create(user=self.user, role=self.role)

        # Crear otra persona para listar
        from apps.institutions.models import DocumentType
        doc_type, _ = DocumentType.objects.get_or_create(code="CC", defaults={"name": "Cedula"})
        self.other_person = Person.objects.create(
            document_type=doc_type,
            document_number="88888888",
            names="Juanito",
            last_names="Gomez",
            email="juanito@example.com",
        )

    def test_list_persons_authenticated(self):
        """Un usuario autorizado puede listar personas."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/accounts/persons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        
        # Deben listarse al menos la persona asociada al usuario y other_person
        results = response.data["data"]["results"]
        self.assertTrue(len(results) >= 2)

    def test_retrieve_person_detail(self):
        """Un usuario autorizado puede ver el detalle de una persona."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/accounts/persons/{self.other_person.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["names"], "Juanito")

    def test_persons_read_only(self):
        """La API de personas es exclusivamente de lectura (no permite POST, PUT, DELETE)."""
        self.client.force_authenticate(user=self.user)
        data = {
            "document_number": "77777777",
            "names": "Prohibido",
            "last_names": "Intento",
        }
        
        # Intentar POST (bloqueado por permisos con 403 ya que create no está en action_permissions)
        response_post = self.client.post("/api/accounts/persons/", data, format="json")
        self.assertEqual(response_post.status_code, status.HTTP_403_FORBIDDEN)

        # Intentar DELETE (bloqueado por permisos con 403 ya que destroy no está en action_permissions)
        response_delete = self.client.delete(f"/api/accounts/persons/{self.other_person.id}/")
        self.assertEqual(response_delete.status_code, status.HTTP_403_FORBIDDEN)


class FilterAPITest(TestCase):
    """Tests para validación de filtros avanzados del módulo accounts (django-filter)."""

    def setUp(self):
        self.client = APIClient()
        # Admin superusuario para omitir permisos y enfocarse exclusivamente en filtros
        self.admin = create_test_user(
            email="admin@example.com",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.admin)

        # Crear Roles
        self.role_active = Role.objects.create(name="Rol Activo", code="R_ACT", active=True)
        self.role_inactive = Role.objects.create(name="Rol Inactivo", code="R_INA", active=False)

        # Crear Permisos
        self.perm_grading = Permission.objects.create(code="grading.test", module="grading")
        self.perm_academic = Permission.objects.create(code="academic.test", module="academic")

        # Crear Usuarios con sus estados
        self.user_active = create_test_user(
            email="activo@example.com",
            dni="DNI-ACTIVO",
            active=True,
        )
        UserRole.objects.create(user=self.user_active, role=self.role_active)

        self.user_inactive = create_test_user(
            email="inactivo@example.com",
            dni="DNI-INACTIVO",
            active=False,
        )
        UserRole.objects.create(user=self.user_inactive, role=self.role_inactive)

    def test_filter_permissions_by_module(self):
        """Filtra permisos por módulo utilizando iexact."""
        response = self.client.get("/api/accounts/permissions/?module=GRADING")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["code"], "grading.test")

    def test_filter_roles_by_active_status(self):
        """Filtra roles activos e inactivos."""
        # Roles activos
        response_active = self.client.get("/api/accounts/roles/?active=true")
        self.assertEqual(response_active.status_code, status.HTTP_200_OK)
        results_active = response_active.data["data"]["results"]
        # Debe incluir al menos el rol activo y el creado en setUp
        self.assertTrue(any(r["id"] == self.role_active.id for r in results_active))
        self.assertFalse(any(r["id"] == self.role_inactive.id for r in results_active))

        # Roles inactivos
        response_inactive = self.client.get("/api/accounts/roles/?active=false")
        self.assertEqual(response_inactive.status_code, status.HTTP_200_OK)
        results_inactive = response_inactive.data["data"]["results"]
        self.assertEqual(len(results_inactive), 1)
        self.assertEqual(results_inactive[0]["id"], self.role_inactive.id)

    def test_filter_users_by_active_status_and_dni_and_role(self):
        """Filtra usuarios por active, role_id y dni."""
        # Filtrar activos
        response_active = self.client.get("/api/accounts/users/?active=true")
        self.assertEqual(response_active.status_code, status.HTTP_200_OK)
        results_active = response_active.data["data"]["results"]
        self.assertTrue(any(u["id"] == self.user_active.id for u in results_active))
        self.assertFalse(any(u["id"] == self.user_inactive.id for u in results_active))

        # Filtrar por dni (iexact)
        response_dni = self.client.get("/api/accounts/users/?dni=dni-inactivo")
        self.assertEqual(response_dni.status_code, status.HTTP_200_OK)
        results_dni = response_dni.data["data"]["results"]
        self.assertEqual(len(results_dni), 1)
        self.assertEqual(results_dni[0]["id"], self.user_inactive.id)

        # Filtrar por role_id
        response_role = self.client.get(f"/api/accounts/users/?role_id={self.role_active.id}")
        self.assertEqual(response_role.status_code, status.HTTP_200_OK)
        results_role = response_role.data["data"]["results"]
        self.assertEqual(len(results_role), 1)
        self.assertEqual(results_role[0]["id"], self.user_active.id)
