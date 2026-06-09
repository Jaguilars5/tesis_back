from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.iam.models import Permission, Role, RolePermission, User, UserRole
from apps.core.tests.helpers import create_test_user


class AnalyticsViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.perm = Permission.objects.create(
            code="analytics.view_risk_score", module="analytics",
        )
        self.role = Role.objects.create(name="Test Role")
        RolePermission.objects.create(role=self.role, permission=self.perm)

        self.user = create_test_user(
            email="test@test.com", dni="1234567890",
            names="Test", last_names="User",
        )
        UserRole.objects.create(user=self.user, role=self.role)

    def test_list_requires_auth(self):
        response = self.client.get("/api/analytics/student-risk-scores/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_with_permission(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/analytics/student-risk-scores/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_without_permission(self):
        user_no_perm = create_test_user(
            email="noperm@test.com", dni="0000000000",
            names="No", last_names="Perm",
        )
        self.client.force_authenticate(user=user_no_perm)
        response = self.client.get("/api/analytics/student-risk-scores/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
