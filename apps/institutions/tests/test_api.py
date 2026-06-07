from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from django.contrib.auth import get_user_model
from apps.accounts.models import Role
from apps.core.tests.helpers import create_test_user
from ..models import DocumentType, School_Year

User = get_user_model()


class SchoolYearAPITest(APITestCase):
    """Tests para los endpoints API de School_Year"""

    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="schoolyear@test.com",
            dni="1818181818",
            names="School",
            last_names="Tester",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.url = "/api/institutions/school-year/"

    def test_list_school_years(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_school_year(self):
        data = {
            "name": "2025-2026",
            "start_date": "2025-09-01",
            "end_date": "2026-07-31",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_school_year(self):
        response = self.client.get(f"{self.url}{self.school_year.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_school_year(self):
        data = {"name": "2024-2025 Modified"}
        response = self.client.patch(
            f"{self.url}{self.school_year.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DocumentTypeAPITest(APITestCase):
    """Tests para los endpoints de DocumentType"""

    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="doctype@test.com",
            dni="2010101010",
            names="DocType",
            last_names="Tester",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        DocumentType.objects.create(code="PP", name="Pasaporte")
        self.url = "/api/institutions/document-types/"

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data.get("data", [])), 2)

    def test_retrieve(self):
        doc = DocumentType.objects.first()
        response = self.client.get(f"{self.url}{doc.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["data"]["code"], "CC")

    def test_create_not_allowed(self):
        data = {"code": "TI", "name": "Tarjeta de Identidad"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
