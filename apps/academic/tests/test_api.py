from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from apps.institutions.models import AcademicGrade, AcademicLevel, School_Year
from apps.institutions.models import Section
from apps.academic.models import Subject
from apps.accounts.models import Role, User
from apps.core.tests.helpers import create_test_user


class AcademicAPITest(APITestCase):
    """Tests para los endpoints API de Academic"""

    def setUp(self):
        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level, name="6to", sequence_order=6
        )
        role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="academic@test.com",
            dni="1717171717",
            names="Academic",
            last_names="Tester",
            password="test_password_123",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.section_url = "/api/academic/section/"

    def test_list_sections(self):
        Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=40,
        )
        response = self.client.get(self.section_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_section(self):
        data = {
            "school_year": self.school_year.id,
            "academic_grade": self.academic_grade.id,
            "parallel": "A",
            "capacity": 40,
        }
        response = self.client.post(self.section_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_section(self):
        section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=40,
        )
        response = self.client.get(f"{self.section_url}{section.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_section(self):
        section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=40,
        )
        data = {"capacity": 35}
        response = self.client.patch(f"{self.section_url}{section.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_subjects(self):
        Subject.objects.create(name="Matemáticas", code="MAT-001")
        response = self.client.get("/api/academic/subject/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_subject(self):
        data = {"name": "Lengua", "code": "LEN-001"}
        response = self.client.post("/api/academic/subject/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_subject(self):
        subject = Subject.objects.create(name="Ciencias", code="CIE-001")
        response = self.client.get(f"/api/academic/subject/{subject.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_subject(self):
        subject = Subject.objects.create(name="Historia", code="HIS-001")
        data = {"name": "Historia Universal"}
        response = self.client.patch(f"/api/academic/subject/{subject.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
