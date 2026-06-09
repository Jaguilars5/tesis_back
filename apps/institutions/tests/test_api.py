from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from django.contrib.auth import get_user_model
from apps.iam.models import Role
from apps.core.tests.helpers import create_test_user
from ..models import AcademicLevel, AcademicGrade, SchoolYear, Section

User = get_user_model()


class SchoolYearAPITest(APITestCase):
    """Tests para los endpoints API de SchoolYear"""

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
        self.school_year = SchoolYear.objects.create(
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


class SectionAPITest(APITestCase):
    """Tests para los endpoints API de Section"""

    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="section@test.com",
            dni="1919191919",
            names="Section",
            last_names="Tester",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.school_year = SchoolYear.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            parallel="A",
            capacity=30,
            code="SEC_A",
        )
        self.url = "/api/institutions/section/"

    def test_list_sections(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_section(self):
        data = {
            "school_year": self.school_year.id,
            "parallel": "B",
            "capacity": 25,
            "code": "SEC_B",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_section(self):
        response = self.client.get(f"{self.url}{self.section.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_section(self):
        data = {"parallel": "C"}
        response = self.client.patch(
            f"{self.url}{self.section.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_soft_delete_section(self):
        response = self.client.post(f"{self.url}{self.section.id}/soft-delete/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AcademicLevelAPITest(APITestCase):
    """Tests para los endpoints API de AcademicLevel"""

    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="academiclevel@test.com",
            dni="2020202020",
            names="Level",
            last_names="Tester",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.level = AcademicLevel.objects.create(name="Primaria", code="PRIM")
        self.url = "/api/institutions/academic-levels/"

    def test_list_academic_levels(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_academic_level(self):
        data = {"name": "Secundaria", "code": "SEC"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_academic_level(self):
        response = self.client.get(f"{self.url}{self.level.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_academic_level(self):
        data = {"name": "Primaria Modificada"}
        response = self.client.patch(
            f"{self.url}{self.level.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_academic_level(self):
        response = self.client.delete(f"{self.url}{self.level.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AcademicGradeAPITest(APITestCase):
    """Tests para los endpoints API de AcademicGrade"""

    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="academicgrade@test.com",
            dni="2121212121",
            names="Grade",
            last_names="Tester",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.level = AcademicLevel.objects.create(name="Primaria", code="PRIM")
        self.grade = AcademicGrade.objects.create(
            name="5to", sequence_order=5, code="5TO"
        )
        self.url = "/api/institutions/academic-grades/"

    def test_list_academic_grades(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_academic_grade(self):
        data = {"name": "6to", "sequence_order": 6, "code": "6TO"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_academic_grade(self):
        response = self.client.get(f"{self.url}{self.grade.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_academic_grade(self):
        data = {"name": "5to Modificado"}
        response = self.client.patch(
            f"{self.url}{self.grade.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_academic_grade(self):
        response = self.client.delete(f"{self.url}{self.grade.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

