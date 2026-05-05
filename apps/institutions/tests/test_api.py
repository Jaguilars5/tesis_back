from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from django.contrib.auth import get_user_model
from apps.accounts.models import Role
from ..models import Institution, School_Year, Classroom

User = get_user_model()


class InstitutionAPITest(APITestCase):
    """Tests para los endpoints API de Institution"""

    def setUp(self):
        self.institution = Institution.objects.create(
            name="Instituto Test",
            code="IT-001",
            address="Calle Principal",
            city="Quito",
        )
        self.role = Role.objects.create(name="Admin")
        self.user = User.objects.create_user(
            email="institutions@test.com",
            dni="1717171717",
            names="Institutions",
            last_names="Tester",
            password="test_password_123",
            role=self.role,
            institution=self.institution,
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/institutions/institution/"

    def test_list_institutions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_institution(self):
        data = {
            "name": "Nueva Institución",
            "code": "NI-002",
            "address": "Av. Nueva",
            "city": "Guayaquil",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_institution(self):
        response = self.client.get(f"{self.url}{self.institution.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_institution(self):
        data = {"name": "Instituto Actualizado"}
        response = self.client.patch(
            f"{self.url}{self.institution.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_institution(self):
        institution = Institution.objects.create(
            name="Para Eliminar", code="PE-001", address="Dirección", city="Quito"
        )
        response = self.client.delete(f"{self.url}{institution.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SchoolYearAPITest(APITestCase):
    """Tests para los endpoints API de School_Year"""

    def setUp(self):
        self.institution = Institution.objects.create(
            name="Escuela A", code="EA-001", address="Dirección", city="Quito"
        )
        self.role = Role.objects.create(name="Admin")
        self.user = User.objects.create_user(
            email="schoolyear@test.com",
            dni="1818181818",
            names="School",
            last_names="Tester",
            password="test_password_123",
            role=self.role,
            institution=self.institution,
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.school_year = School_Year.objects.create(
            institution=self.institution,
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
            "institution": self.institution.id,
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


class ClassroomAPITest(APITestCase):
    """Tests para los endpoints API de Classroom"""

    def setUp(self):
        self.institution = Institution.objects.create(
            name="Instituto B", code="IB-002", address="Dirección B", city="Quito"
        )
        self.role = Role.objects.create(name="Admin")
        self.user = User.objects.create_user(
            email="classroom@test.com",
            dni="1919191919",
            names="Classroom",
            last_names="Tester",
            password="test_password_123",
            role=self.role,
            institution=self.institution,
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.classroom = Classroom.objects.create(
            institution=self.institution,
            name="101",
            room_type="Aula de clase",
            capacity=40,
        )
        self.url = "/api/institutions/classroom/"

    def test_list_classrooms(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_classroom(self):
        data = {
            "institution": self.institution.id,
            "name": "102",
            "room_type": "Aula de clase",
            "capacity": 35,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_classroom(self):
        response = self.client.get(f"{self.url}{self.classroom.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_classroom(self):
        data = {"capacity": 50}
        response = self.client.patch(
            f"{self.url}{self.classroom.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_classroom_capacity_validation(self):
        data = {
            "institution": self.institution.id,
            "name": "Invalid",
            "room_type": "Aula",
            "capacity": 0,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
