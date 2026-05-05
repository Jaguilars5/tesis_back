from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from apps.accounts.models import Permission, Role, RolePermission, User, UserPermission
from apps.core.permissions import HasPermission, require_permission
from apps.institutions.models import Institution


class MockViewSet:
    action = "list"
    action_permissions = {
        "list": "test.view_mock",
        "create": "test.create_mock",
    }


class HasPermissionTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.institution = Institution.objects.create(
            name="Test Institution", code="TST-001",
            address="Test St", city="Quito",
        )
        self.permission = Permission.objects.create(
            codename="test.view_mock", description="View mock", module="test",
        )
        self.perm_create = Permission.objects.create(
            codename="test.create_mock", description="Create mock", module="test",
        )
        self.role = Role.objects.create(name="Test Role")
        RolePermission.objects.create(role=self.role, permission=self.permission)

        self.user_with_perm = User.objects.create_user(
            email="withperm@test.com", dni="1000000000",
            names="With", last_names="Perm",
            password="testpass123", institution=self.institution,
            role=self.role,
        )
        self.user_without_perm = User.objects.create_user(
            email="noperm@test.com", dni="1000000001",
            names="No", last_names="Perm",
            password="testpass123", institution=self.institution,
        )
        self.superuser = User.objects.create_superuser(
            email="super@test.com", dni="1000000002",
            names="Super", last_names="User",
            password="testpass123", institution=self.institution,
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

    def test_permission_via_user_permission_override(self):
        UserPermission.objects.create(
            user=self.user_without_perm,
            permission=self.permission,
            granted=True,
        )
        request = self._make_request(user=self.user_without_perm)
        result = HasPermission().has_permission(request, self.mock_view)
        self.assertTrue(result)

    def test_permission_revoked_via_user_permission(self):
        UserPermission.objects.create(
            user=self.user_with_perm,
            permission=self.permission,
            granted=False,
        )
        request = self._make_request(user=self.user_with_perm)
        result = HasPermission().has_permission(request, self.mock_view)
        self.assertFalse(result)


class RequirePermissionTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.institution = Institution.objects.create(
            name="Test Institution", code="TST-001",
            address="Test St", city="Quito",
        )
        self.permission = Permission.objects.create(
            codename="test.require_perm",
            description="Require perm",
            module="test",
        )
        self.role = Role.objects.create(name="Test Role")
        RolePermission.objects.create(role=self.role, permission=self.permission)

        self.user_with_perm = User.objects.create_user(
            email="withperm@test.com", dni="2000000000",
            names="With", last_names="Perm",
            password="testpass123", institution=self.institution,
            role=self.role,
        )
        self.user_without_perm = User.objects.create_user(
            email="noperm@test.com", dni="2000000001",
            names="No", last_names="Perm",
            password="testpass123", institution=self.institution,
        )

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
