"""
Tests de lógica de negocio para los services del módulo accounts.

Prueban UserService, RoleService y PermissionService con mocks cuando es necesario.
"""

from django.test import TestCase
from apps.accounts.services.user_service import UserService
from apps.accounts.services.role_service import RoleService
from apps.accounts.services.permission_service import PermissionService
from apps.accounts.models import User, Role, Permission


class UserServiceTest(TestCase):
    """Tests para UserService."""

    def setUp(self):
        self.role = Role.objects.create(name="Docente", description="Rol de docente")
        self.service = UserService()

    def test_create_user(self):
        """Verifica que create_user funciona correctamente."""
        user = self.service.create_user(
            document_number="123456789",
            names="Juan",
            last_names="Pérez",
            email="juan@example.com",
            password="micontraseña123",
            role_id=self.role.id,
        )

        self.assertEqual(user.email, "juan@example.com")
        self.assertTrue(user.check_password("micontraseña123"))

    def test_create_user_duplicate_email(self):
        """Verifica que create_user lanza error con email duplicado."""
        self.service.create_user(
            document_number="123456789",
            names="Juan",
            last_names="Pérez",
            email="juan@example.com",
            password="micontraseña123",
            role_id=self.role.id,
        )

        with self.assertRaises(ValueError) as context:
            self.service.create_user(
                document_number="987654321",
                names="Pedro",
                last_names="García",
                email="juan@example.com",
                password="micontraseña123",
                role_id=self.role.id,
            )

        self.assertIn("ya está registrado", str(context.exception))

    def test_create_user_invalid_role(self):
        """Verifica que create_user lanza error con rol inexistente."""
        with self.assertRaises(ValueError) as context:
            self.service.create_user(
                document_number="123456789",
                names="Juan",
                last_names="Pérez",
                email="juan@example.com",
                password="micontraseña123",
                role_id=9999,
            )

        self.assertIn("no existe", str(context.exception))

    def test_get_user(self):
        """Verifica que get_user retorna un usuario."""
        user = self.service.create_user(
            document_number="123456789",
            names="Juan",
            last_names="Pérez",
            email="juan@example.com",
            password="micontraseña123",
            role_id=self.role.id,
        )

        retrieved = self.service.get_user(user.id)
        self.assertEqual(retrieved.id, user.id)

    def test_change_password(self):
        """Verifica que change_password funciona."""
        user = self.service.create_user(
            document_number="123456789",
            names="Juan",
            last_names="Pérez",
            email="juan@example.com",
            password="micontraseña123",
            role_id=self.role.id,
        )

        self.service.change_password(user.id, "nuevacontraseña456")
        user.refresh_from_db()
        self.assertTrue(user.check_password("nuevacontraseña456"))


class RoleServiceTest(TestCase):
    """Tests para RoleService."""

    def setUp(self):
        self.service = RoleService()

    def test_create_role(self):
        """Verifica que create_role funciona correctamente."""
        role = self.service.create_role(name="Docente", description="Rol de docente")

        self.assertEqual(role.name, "Docente")
        self.assertTrue(role.active)

    def test_create_role_duplicate_name(self):
        """Verifica que create_role lanza error con nombre duplicado."""
        self.service.create_role(name="Docente")

        with self.assertRaises(ValueError) as context:
            self.service.create_role(name="Docente")

        self.assertIn("ya existe", str(context.exception))

    def test_add_permission_to_role(self):
        """Verifica que add_permission_to_role funciona."""
        role = self.service.create_role(name="Docente")
        permission = Permission.objects.create(
            code="grading.create_note", module="grading"
        )

        rp, created = self.service.add_permission_to_role(
            role.id, "grading.create_note"
        )

        self.assertTrue(created)
        perms = self.service.get_role_permissions(role.id)
        self.assertEqual(perms.count(), 1)

    def test_assign_permissions_to_role(self):
        """Verifica que assign_permissions_to_role funciona."""
        role = self.service.create_role(name="Docente")
        perm1 = Permission.objects.create(code="perm1", module="test")
        perm2 = Permission.objects.create(code="perm2", module="test")
        perm3 = Permission.objects.create(code="perm3", module="test")

        count = self.service.assign_permissions_to_role(role.id, ["perm1", "perm2"])

        self.assertEqual(count, 2)
        perms = self.service.get_role_permissions(role.id)
        self.assertEqual(perms.count(), 2)


class PermissionServiceTest(TestCase):
    """Tests para PermissionService."""

    def setUp(self):
        self.service = PermissionService()

    def test_create_permission(self):
        """Verifica que create_permission funciona correctamente."""
        permission = self.service.create_permission(
            code="grading.create_note", description="Crear notas", module="grading"
        )

        self.assertEqual(permission.code, "grading.create_note")

    def test_create_permission_duplicate_code(self):
        """Verifica que create_permission lanza error con code duplicado."""
        self.service.create_permission(code="grading.create_note")

        with self.assertRaises(ValueError) as context:
            self.service.create_permission(code="grading.create_note")

        self.assertIn("ya existe", str(context.exception))

    def test_create_permissions_bulk(self):
        """Verifica que create_permissions_bulk funciona."""
        permission_list = [
            {"code": "perm1", "description": "Permiso 1", "module": "test"},
            {"code": "perm2", "description": "Permiso 2", "module": "test"},
        ]

        perms = self.service.create_permissions_bulk(permission_list)

        self.assertEqual(len(perms), 2)

    def test_list_permissions(self):
        """Verifica que list_permissions funciona."""
        self.service.create_permission("perm1", module="test")
        self.service.create_permission("perm2", module="test")

        perms = self.service.list_permissions()
        self.assertEqual(perms.count(), 2)
