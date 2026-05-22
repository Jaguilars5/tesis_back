"""
Tests unitarios para los modelos del módulo accounts.

Prueban validaciones de campo, propiedades calculadas y restricciones de BD.
"""

from django.test import TestCase
from apps.accounts.models import User, Role, Permission, RolePermission
from apps.core.tests.helpers import create_test_user


class PermissionModelTest(TestCase):
    """Tests para el modelo Permission."""

    def setUp(self):
        self.permission = Permission.objects.create(
            code="grading.create_note", description="Crear notas", module="grading"
        )

    def test_create_permission(self):
        """Verifica que se crea un permiso correctamente."""
        self.assertEqual(self.permission.code, "grading.create_note")
        self.assertEqual(self.permission.description, "Crear notas")
        self.assertEqual(self.permission.module, "grading")

    def test_permission_unique_code(self):
        """Verifica que el code es único."""
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            Permission.objects.create(
                code="grading.create_note", description="Duplicado"
            )

    def test_permission_str(self):
        """Verifica la representación en string."""
        self.assertEqual(str(self.permission), "grading.create_note")


class RoleModelTest(TestCase):
    """Tests para el modelo Role."""

    def setUp(self):
        self.role = Role.objects.create(
            name="Docente", description="Rol de docente", active=True
        )
        self.permission = Permission.objects.create(
            code="grading.create_note", module="grading"
        )
        RolePermission.objects.create(role=self.role, permission=self.permission)

    def test_create_role(self):
        """Verifica que se crea un rol correctamente."""
        self.assertEqual(self.role.name, "Docente")
        self.assertTrue(self.role.active)

    def test_role_unique_name(self):
        """Verifica que el nombre del rol es único."""
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            Role.objects.create(name="Docente")

    def test_role_get_all_permissions(self):
        """Verifica que se obtienen todos los permisos del rol."""
        perms = self.role.get_all_permissions()
        self.assertEqual(perms.count(), 1)
        self.assertIn(self.permission, perms)

    def test_role_str(self):
        """Verifica la representación en string."""
        self.assertEqual(str(self.role), "Docente")


class UserModelTest(TestCase):
    """Tests para el modelo User."""

    def setUp(self):
        self.role = Role.objects.create(name="Docente", description="Rol de docente")
        self.user = create_test_user(
            email="juan@example.com",
            dni="123456789",
            names="Juan",
            last_names="Pérez",
        )

    def test_create_user(self):
        """Verifica que se crea un usuario correctamente."""
        self.assertEqual(self.user.person.document_number, "123456789")
        self.assertEqual(self.user.person.names, "Juan")
        self.assertEqual(self.user.email, "juan@example.com")

    def test_user_email_unique(self):
        """Verifica que el email es único."""
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            create_test_user(
                email="juan@example.com",
                dni="987654321",
                names="Pedro",
                last_names="García",
            )

    def test_user_dni_unique(self):
        """Verifica que el DNI es único."""
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            create_test_user(
                email="pedro@example.com",
                dni="123456789",
                names="Pedro",
                last_names="García",
            )

    def test_set_password(self):
        """Verifica que la contraseña se hashea correctamente."""
        self.user.set_password("micontraseña123")
        self.assertTrue(self.user.check_password("micontraseña123"))
        self.assertFalse(self.user.check_password("contraseniaincorrecta"))

    def test_check_password(self):
        """Verifica que check_password funciona correctamente."""
        self.user.set_password("micontraseña123")
        self.assertTrue(self.user.check_password("micontraseña123"))

    def test_user_str(self):
        """Verifica la representación en string."""
        expected = f"Juan Pérez (juan@example.com)"
        self.assertEqual(str(self.user), expected)

    def test_has_perm_via_role(self):
        """Verifica que un usuario hereda permisos del rol."""
        from apps.accounts.models import UserRole

        UserRole.objects.create(user=self.user, role=self.role)
        permission = Permission.objects.create(
            code="grading.create_note", module="grading"
        )
        RolePermission.objects.create(role=self.role, permission=permission)

        self.assertTrue(self.user.has_perm("grading.create_note"))


