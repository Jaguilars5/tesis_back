from django.test import TestCase
from apps.iam.models import User, Role, Permission, UserRole, RolePermission
from apps.iam.infrastructure.repositories import (
    UserRepository,
    RoleRepository,
    PermissionRepository,
)


class UserRepositoryTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="admin123",
        )

    def test_get_by_id(self):
        user = UserRepository.get_by_id(self.admin.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "admin")

    def test_get_by_id_not_found(self):
        self.assertIsNone(UserRepository.get_by_id(9999))

    def test_get_by_username(self):
        user = UserRepository.get_by_username("admin")
        self.assertIsNotNone(user)

    def test_get_by_username_not_found(self):
        self.assertIsNone(UserRepository.get_by_username("nonexistent"))

    def test_get_all_active(self):
        users = UserRepository.get_all_active()
        self.assertGreaterEqual(len(users), 1)

    def test_search(self):
        results = UserRepository.search("admin")
        self.assertGreaterEqual(len(results), 1)


class RoleRepositoryTest(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Test Role", code="TEST")

    def test_get_by_id(self):
        role = RoleRepository.get_by_id(self.role.id)
        self.assertIsNotNone(role)

    def test_get_by_name(self):
        role = RoleRepository.get_by_name("Test Role")
        self.assertIsNotNone(role)

    def test_get_all_active(self):
        roles = RoleRepository.get_all_active()
        self.assertGreaterEqual(len(roles), 1)

    def test_get_cascade_counts(self):
        counts = RoleRepository.get_cascade_counts(self.role.id)
        self.assertIsInstance(counts, dict)


class PermissionRepositoryTest(TestCase):
    def setUp(self):
        self.perm = Permission.objects.create(code="test.view", module="test")

    def test_get_by_code(self):
        perm = PermissionRepository.get_by_code("test.view")
        self.assertIsNotNone(perm)

    def test_get_by_module(self):
        perms = PermissionRepository.get_by_module("test")
        self.assertEqual(len(perms), 1)

    def test_count_role_permissions(self):
        count = PermissionRepository.count_role_permissions(self.perm.id)
        self.assertEqual(count, 0)
