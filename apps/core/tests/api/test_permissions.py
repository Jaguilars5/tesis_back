from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from apps.iam import Permission, Role, RolePermission, User, UserRole
from apps.core.api.permissions import HasPermission, require_permission
from apps.core.tests.helpers import create_test_user


class MockViewSet:
    action = "list"
    action_permissions = {
        "list": "test.view_mock",
        "create": "test.create_mock",
    }


class HasPermissionTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = Permission.objects.create(
            code="test.view_mock", description="View mock", module="test",
        )
        self.perm_create = Permission.objects.create(
            code="test.create_mock", description="Create mock", module="test",
        )
        self.role = Role.objects.create(name="Test Role")
        RolePermission.objects.create(role=self.role, permission=self.permission)

        self.user_with_perm = create_test_user(
            email="withperm@test.com", dni="1000000000",
            names="With", last_names="Perm",
        )
        self.user_without_perm = create_test_user(
            email="noperm@test.com", dni="1000000001",
            names="No", last_names="Perm",
        )
        UserRole.objects.create(user=self.user_with_perm, role=self.role)
        self.superuser = create_test_user(
            email="super@test.com", dni="1000000002",
            names="Super", last_names="User",
            is_superuser=True,
        )
        self.mock_view = MockViewSet()

    def _make_request(self, method="get", user=None):
        request = getattr(self.factory, method)("/mock/")
        request.user = user if user is not None else AnonymousUser()
        return request

    def test_superuser_always_has_access(self):
        request = self._make_request(user=self.superuser)
        result = HasPermission().has_permission(request, self.mock_view)
        self.assertTrue(result)

    def test_user_with_permission_has_access(self):
        request = self._make_request(user=self.user_with_perm)
        result = HasPermission().has_permission(request, self.mock_view)
        self.assertTrue(result)

    def test_user_without_permission_denied(self):
        request = self._make_request(user=self.user_without_perm)
        result = HasPermission().has_permission(request, self.mock_view)
        self.assertFalse(result)

    def test_unauthenticated_denied(self):
        request = self._make_request()
        result = HasPermission().has_permission(request, self.mock_view)
        self.assertFalse(result)

    def test_action_not_mapped_denied(self):
        self.mock_view.action = "update"
        request = self._make_request(method="put", user=self.user_with_perm)
        result = HasPermission().has_permission(request, self.mock_view)
        self.assertFalse(result)


class RequirePermissionTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = Permission.objects.create(
            code="test.require_perm",
            description="Require perm",
            module="test",
        )
        self.role = Role.objects.create(name="Test Role")
        RolePermission.objects.create(role=self.role, permission=self.permission)

        self.user_with_perm = create_test_user(
            email="withperm@test.com", dni="2000000000",
            names="With", last_names="Perm",
        )
        self.user_without_perm = create_test_user(
            email="noperm@test.com", dni="2000000001",
            names="No", last_names="Perm",
        )
        UserRole.objects.create(user=self.user_with_perm, role=self.role)

    def _make_request(self, user=None):
        request = self.factory.get("/mock/")
        request.user = user if user is not None else AnonymousUser()
        return request

    def test_user_with_permission_can_access(self):
        @require_permission("test.require_perm")
        def mock_view(request):
            return Response({"ok": True}, status=200)

        request = self._make_request(user=self.user_with_perm)
        response = mock_view(request)
        self.assertEqual(response.status_code, 200)

    def test_user_without_permission_denied(self):
        @require_permission("test.require_perm")
        def mock_view(request):
            return Response({"ok": True}, status=200)

        request = self._make_request(user=self.user_without_perm)
        with self.assertRaises(PermissionDenied):
            mock_view(request)

    def test_unauthenticated_denied(self):
        @require_permission("test.require_perm")
        def mock_view(request):
            return Response({"ok": True}, status=200)

        request = self._make_request()
        with self.assertRaises(PermissionDenied):
            mock_view(request)
