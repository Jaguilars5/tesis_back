from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date

from apps.iam.models import User, Role, UserRole
from apps.people.models import Person, DocumentType


class SoftDeleteTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="admin123",
        )
        self.client.force_authenticate(user=self.admin)
        self.role = Role.objects.create(name="Test Role", code="TEST")
        doc_type = DocumentType.objects.get_or_create(
            code="CC", defaults={"name": "Cédula de Ciudadanía"}
        )[0]
        person2 = Person.objects.create(
            document_type=doc_type,
            document_number="USER-001",
            names="Test",
            last_names="User",
            email="testuser@test.com",
            birth_date=date(2000, 1, 1),
        )
        self.user = User.objects.create(
            username="testuser",
            person=person2,
        )
        UserRole.objects.create(user=self.user, role=self.role)

    def test_soft_delete_role_requires_confirmation(self):
        response = self.client.post(
            f"/api/iam/roles/{self.role.id}/soft-delete/",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_soft_delete_role_with_confirm(self):
        response = self.client.post(
            f"/api/iam/roles/{self.role.id}/soft-delete/",
            {"confirm": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.role.refresh_from_db()
        self.assertFalse(self.role.is_active)
