"""
Tests unitarios para los modelos del módulo accounts.

Prueban validaciones de campo, propiedades calculadas y restricciones de BD.
"""

from django.test import TestCase
from apps.accounts.models import User, Role, Permission, RolePermission, UserPermission
from apps.institutions.models import Institution


class PermissionModelTest(TestCase):
    """Tests para el modelo Permission."""

    def setUp(self):
        self.permission = Permission.objects.create(
            codename="grading.create_note", description="Crear notas", module="grading"
        )

    def test_create_permission(self):
        """Verifica que se crea un permiso correctamente."""
        self.assertEqual(self.permission.codename, "grading.create_note")
        self.assertEqual(self.permission.description, "Crear notas")
        self.assertEqual(self.permission.module, "grading")

    def test_permission_unique_codename(self):
        """Verifica que el codename es único."""
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            Permission.objects.create(
                codename="grading.create_note", description="Duplicado"
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
            codename="grading.create_note", module="grading"
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
        self.institution = Institution.objects.create(
            name="Institución de Prueba", code="INST001"
        )
        self.role = Role.objects.create(name="Docente", description="Rol de docente")
        self.user = User.objects.create(
            dni="123456789",
            names="Juan",
            last_names="Pérez",
            email="juan@example.com",
            role=self.role,
            institution=self.institution,
            password="password_provisional"
        )

    def test_create_user(self):
        """Verifica que se crea un usuario correctamente."""
        self.assertEqual(self.user.dni, "123456789")
        self.assertEqual(self.user.names, "Juan")
        self.assertEqual(self.user.email, "juan@example.com")

    def test_user_email_unique(self):
        """Verifica que el email es único."""
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            User.objects.create(
                dni="987654321",
                names="Pedro",
                last_names="García",
                email="juan@example.com",
                role=self.role,
                institution=self.institution,
                password="password"
            )

    def test_user_dni_unique_per_institution(self):
        """Verifica que el DNI es único por institución."""
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            User.objects.create(
                dni="123456789",
                names="Pedro",
                last_names="García",
                email="pedro@example.com",
                role=self.role,
                institution=self.institution,
                password="password"
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
        permission = Permission.objects.create(
            codename="grading.create_note", module="grading"
        )
        RolePermission.objects.create(role=self.role, permission=permission)

        self.assertTrue(self.user.has_perm("grading.create_note"))

    def test_has_perm_override_granted(self):
        """Verifica que UserPermission granted=True otorga permiso."""
        permission = Permission.objects.create(
            codename="grading.delete_note", module="grading"
        )
        UserPermission.objects.create(
            user=self.user, permission=permission, granted=True
        )

        self.assertTrue(self.user.has_perm("grading.delete_note"))

    def test_has_perm_override_revoked(self):
        """Verifica que UserPermission granted=False revoca permiso."""
        permission = Permission.objects.create(
            codename="grading.create_note", module="grading"
        )
        RolePermission.objects.create(role=self.role, permission=permission)
        UserPermission.objects.create(
            user=self.user, permission=permission, granted=False
        )

        self.assertFalse(self.user.has_perm("grading.create_note"))

    def test_get_all_permissions(self):
        """Verifica que se obtienen todos los permisos del usuario."""
        perm1 = Permission.objects.create(codename="perm1", module="test")
        perm2 = Permission.objects.create(codename="perm2", module="test")
        perm3 = Permission.objects.create(codename="perm3", module="test")

        # Agregar perm1 al rol
        RolePermission.objects.create(role=self.role, permission=perm1)

        # Agregar perm2 directamente al usuario
        UserPermission.objects.create(user=self.user, permission=perm2, granted=True)

        # Revocar perm1 al usuario
        UserPermission.objects.create(user=self.user, permission=perm1, granted=False)

        perms = self.user.get_all_permissions()
        self.assertIn("perm2", perms)
        self.assertNotIn("perm1", perms)


class UserPermissionModelTest(TestCase):
    """Tests para el modelo UserPermission."""

    def setUp(self):
        self.institution = Institution.objects.create(
            name="Institución de Prueba", code="INST001"
        )
        self.role = Role.objects.create(name="Docente")
        self.user = User.objects.create(
            dni="123456789",
            names="Juan",
            last_names="Pérez",
            email="juan@example.com",
            role=self.role,
            institution=self.institution,
            password="password"
        )
        self.permission = Permission.objects.create(
            codename="grading.create_note", module="grading"
        )

    def test_create_user_permission(self):
        """Verifica que se crea un UserPermission correctamente."""
        up = UserPermission.objects.create(
            user=self.user, permission=self.permission, granted=True, reason="Prueba"
        )
        self.assertEqual(up.user, self.user)
        self.assertEqual(up.permission, self.permission)
        self.assertTrue(up.granted)

    def test_user_permission_unique_together(self):
        """Verifica que (user, permission) es único."""
        from django.db import IntegrityError

        UserPermission.objects.create(
            user=self.user, permission=self.permission, granted=True
        )
        with self.assertRaises(IntegrityError):
            UserPermission.objects.create(
                user=self.user, permission=self.permission, granted=False
            )

    def test_is_expired(self):
        """Verifica que is_expired() funciona."""
        from django.utils import timezone
        from datetime import timedelta

        # Sin expiración
        up = UserPermission.objects.create(
            user=self.user, permission=self.permission, granted=True
        )
        self.assertFalse(up.is_expired())

        # Expirado
        up_expired = UserPermission.objects.create(
            user=User.objects.create(
                dni="987654321",
                names="Pedro",
                last_names="García",
                email="pedro@example.com",
                role=self.role,
                institution=self.institution,
                password="password"
            ),
            permission=self.permission,
            granted=True,
            expires_at=timezone.now() - timedelta(days=1),
        )
        self.assertTrue(up_expired.is_expired())
