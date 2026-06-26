from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date

from apps.iam.models import User, Role, Permission
from apps.people.models import Person, DocumentType


class PermissionIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.role = Role.objects.create(name="Test Role", code="TEST")
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="admin123",
        )

    def test_unauthenticated_user_gets_401(self):
        self.client.logout()
        response = self.client.get("/api/iam/users/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_without_permission_gets_403(self):
        doc_type = DocumentType.objects.get_or_create(
            code="CC", defaults={"name": "Cédula de Ciudadanía"}
        )[0]
        person = Person.objects.create(
            document_type=doc_type,
            document_number="PLAIN-001",
            names="Plain",
            last_names="User",
            email="plain@test.com",
            birth_date=date(2000, 1, 1),
        )
        plain_user = User.objects.create(
            username="plain",
            person=person,
        )
        plain_user.set_password("test1234")
        plain_user.save()
        self.client.force_authenticate(user=plain_user)
        response = self.client.get("/api/iam/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_bypasses_permissions(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/iam/permissions/",
            {"code": "test.super", "module": "test"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
