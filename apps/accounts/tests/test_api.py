"""
Tests de integración HTTP para los endpoints del módulo accounts.

Prueban los endpoints de punta a punta usando APIClient de DRF.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User, Role, Permission
from apps.core.tests.helpers import create_test_user
from apps.institutions.models import Institution


class PermissionAPITest(TestCase):
    """Tests para los endpoints de Permission."""

    def setUp(self):
        self.client = APIClient()
        self.institution = Institution.objects.create(
            name="Institución de Prueba", code="INST001"
        )
        self.role = Role.objects.create(name="Admin")
        self.admin_user = create_test_user(
            email="admin@example.com",
            dni="999999999",
            names="Admin",
            last_names="User",
            institution=self.institution,
            is_superuser=True,
            password="adminpass",
        )

        self.client.force_authenticate(user=self.admin_user)

    def test_list_permissions(self):
        """Verifica que se pueden listar permisos."""
        Permission.objects.create(codename="perm1", module="test")

        response = self.client.get("/api/accounts/permissions/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_permission(self):
        """Verifica que se puede crear un permiso."""
        data = {
            "codename": "grading.create_note",
            "description": "Crear notas",
            "module": "grading",
        }

        response = self.client.post("/api/accounts/permissions/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Permission.objects.count(), 1)

    def test_create_permission_duplicate_codename(self):
        """Verifica que no se puede crear permiso con codename duplicado."""
        Permission.objects.create(codename="perm1")

        data = {"codename": "perm1"}
        response = self.client.post("/api/accounts/permissions/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RoleAPITest(TestCase):
    """Tests para los endpoints de Role."""

    def setUp(self):
        self.client = APIClient()
        self.institution = Institution.objects.create(
            name="Institución de Prueba", code="INST001"
        )
        self.role = Role.objects.create(name="Admin")
        self.admin_user = create_test_user(
            email="admin@example.com",
            dni="999999999",
            names="Admin",
            last_names="User",
            institution=self.institution,
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_list_roles(self):
        """Verifica que se pueden listar roles."""
        response = self.client.get("/api/accounts/roles/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_role(self):
        """Verifica que se puede crear un rol."""
        data = {"name": "Docente", "description": "Rol de docente"}

        response = self.client.post("/api/accounts/roles/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Role.objects.filter(name="Docente").count(), 1)

    def test_add_permission_to_role(self):
        """Verifica que se puede agregar un permiso a un rol."""
        role = Role.objects.create(name="Docente")
        permission = Permission.objects.create(codename="perm1", module="test")

        data = {"permission_codename": "perm1"}
        response = self.client.post(
            f"/api/accounts/roles/{role.id}/add-permission/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserAPITest(TestCase):
    """Tests para los endpoints de User."""

    def setUp(self):
        self.client = APIClient()
        self.institution = Institution.objects.create(
            name="Institución de Prueba", code="INST001"
        )
        self.role = Role.objects.create(name="Admin")
        self.admin_user = create_test_user(
            email="admin@example.com",
            dni="999999999",
            names="Admin",
            last_names="User",
            institution=self.institution,
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_list_users(self):
        """Verifica que se pueden listar usuarios."""
        response = self.client.get("/api/accounts/users/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user(self):
        """Verifica que se puede crear un usuario."""
        data = {
            "document_number": "123456789",
            "names": "Juan",
            "last_names": "Pérez",
            "email": "juan@example.com",
            "password": "micontraseña123",
            "role_id": self.role.id,
            "institution_id": self.institution.id,
        }

        response = self.client.post("/api/accounts/users/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(email="juan@example.com").count(), 1)

    def test_create_user_duplicate_email(self):
        """Verifica que no se puede crear usuario con email duplicado."""
        create_test_user(
            email="otro@example.com",
            dni="111111111",
            names="Otro",
            last_names="Usuario",
            institution=self.institution,
        )

        data = {
            "document_number": "123456789",
            "names": "Juan",
            "last_names": "Pérez",
            "email": "otro@example.com",
            "password": "micontraseña123",
            "role_id": self.role.id,
            "institution_id": self.institution.id,
        }

        response = self.client.post("/api/accounts/users/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password(self):
        """Verifica que se puede cambiar la contraseña."""
        user = create_test_user(
            email="juan@example.com",
            dni="123456789",
            names="Juan",
            last_names="Pérez",
            institution=self.institution,
            password="micontraseña123",
        )

        data = {"new_password": "nuevacontraseña456"}
        response = self.client.post(
            f"/api/accounts/users/{user.id}/change-password/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password("nuevacontraseña456"))

    def test_grant_permission(self):
        """Verifica que se puede otorgar un permiso."""
        user = create_test_user(
            email="juan@example.com",
            dni="123456789",
            names="Juan",
            last_names="Pérez",
            institution=self.institution,
        )
        permission = Permission.objects.create(codename="perm1", module="test")

        data = {"permission_codename": "perm1", "reason": "Prueba"}
        response = self.client.post(
            f"/api/accounts/users/{user.id}/grant-permission/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_permissions(self):
        """Verifica que se pueden obtener los permisos de un usuario."""
        user = create_test_user(
            email="juan@example.com",
            dni="123456789",
            names="Juan",
            last_names="Pérez",
            institution=self.institution,
        )

        response = self.client.get(f"/api/accounts/users/{user.id}/permissions/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("permissions", response.data["data"])
