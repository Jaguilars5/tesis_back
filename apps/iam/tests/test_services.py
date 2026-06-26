from django.test import TestCase
from django.contrib.auth.hashers import make_password
from datetime import date

from apps.iam.models import User, Role, Permission, UserRole
from apps.iam.domain.services import (
    UserService,
    RoleService,
    PermissionService,
)
from apps.people.models import Person, DocumentType


class UserServiceTest(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Test Role", code="TEST")
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="admin123",
        )

    def test_get_user_not_found(self):
        with self.assertRaises(ValueError):
            UserService.get_user(9999)

    def test_deactivate_user(self):
        user = UserService.get_user(self.admin.id)
        UserService.deactivate_user(user.id)
        user.refresh_from_db()
        self.assertFalse(user.is_active)


class RoleServiceTest(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Test Role", code="TEST")

    def test_create_role_duplicate(self):
        with self.assertRaises(ValueError):
            RoleService.create_role("Test Role")

    def test_get_role_not_found(self):
        with self.assertRaises(ValueError):
            RoleService.get_role(9999)

    def test_deactivate_role_with_users(self):
        admin = User.objects.create_superuser(
            username="admin2",
            email="admin2@test.com",
            password="admin123",
        )
        UserRole.objects.create(user=admin, role=self.role)
        with self.assertRaises(ValueError):
            RoleService.deactivate_role(self.role.id)


class PermissionServiceTest(TestCase):
    def test_create_permission_duplicate(self):
        Permission.objects.create(code="test.dup", module="test")
        with self.assertRaises(ValueError):
            PermissionService.create_permission("test.dup")

    def test_delete_permission_with_roles(self):
        perm = Permission.objects.create(code="test.delete_me", module="test")
        role = Role.objects.create(name="Test")
        from apps.iam.models import RolePermission
        RolePermission.objects.create(role=role, permission=perm)
        with self.assertRaises(ValueError):
            PermissionService.delete_permission(perm.id)

    def test_get_permission_not_found(self):
        with self.assertRaises(ValueError):
            PermissionService.get_permission(9999)
