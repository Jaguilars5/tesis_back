from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Permission, Role, RolePermission, User


class GradingViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.perm_view = Permission.objects.create(
            codename="grading.view_note", module="grading",
        )
        self.perm_create = Permission.objects.create(
            codename="grading.create_note", module="grading",
        )
        self.role = Role.objects.create(name="Test Role")
        RolePermission.objects.create(role=self.role, permission=self.perm_view)
        RolePermission.objects.create(role=self.role, permission=self.perm_create)

        self.user = User.objects.create_user(
            dni="1234567890", names="Test", last_names="User",
            email="test@test.com", password="testpass123456",
            role=self.role,
        )

    def test_list_requires_auth(self):
        response = self.client.get("/api/grading/student-notes/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_with_permission(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/grading/student-notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_without_permission(self):
        user_no_perm = User.objects.create_user(
            dni="0000000000", names="No", last_names="Perm",
            email="noperm@test.com", password="testpass123456",
        )
        self.client.force_authenticate(user=user_no_perm)
        response = self.client.get("/api/grading/student-notes/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_requires_permission(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/grading/student-notes/", {"student": 999}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
