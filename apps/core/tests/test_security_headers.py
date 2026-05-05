from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Permission, Role, RolePermission, User


class SecurityHeadersTestCase(TestCase):
    def setUp(self):
        perm = Permission.objects.create(
            codename="accounts.view_permission", module="accounts"
        )
        role = Role.objects.create(name="Test Role")
        RolePermission.objects.create(role=role, permission=perm)

        self.user = User.objects.create_user(
            dni="1234567890", names="Test", last_names="User",
            email="test@test.com", password="testpass123456",
            role=role,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_x_content_type_options(self):
        response = self.client.get("/api/accounts/permissions/")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")

    def test_x_frame_options(self):
        response = self.client.get("/api/accounts/permissions/")
        self.assertEqual(response["X-Frame-Options"], "DENY")

    def test_x_xss_protection(self):
        response = self.client.get("/api/accounts/permissions/")
        self.assertEqual(response["X-XSS-Protection"], "1; mode=block")

    def test_referrer_policy(self):
        response = self.client.get("/api/accounts/permissions/")
        self.assertEqual(
            response["Referrer-Policy"], "strict-origin-when-cross-origin"
        )

    def test_permissions_policy(self):
        response = self.client.get("/api/accounts/permissions/")
        self.assertIn("camera=()", response["Permissions-Policy"])
