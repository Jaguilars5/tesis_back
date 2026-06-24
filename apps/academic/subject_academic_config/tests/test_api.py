from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
REPLACED AcademicGrade, AcademicLevel, AcademicSublevel
from apps.academic.subject.infrastructure.models import Subject
from apps.core.tests.helpers import create_test_user


class SubjectAcademicConfigAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="config@test.com", dni="3333333333",
            names="Config", last_names="Tester", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        level = AcademicLevel.objects.create(name="Primaria")
        sublevel = AcademicSublevel.objects.create(academic_level=level, name="Básica")
        self.grade = AcademicGrade.objects.create(academic_sublevel=sublevel, name="6to")
        self.subject = Subject.objects.create(name="Matemáticas", code="MAT-001")
        self.url = "/api/academic/subject-academic-configs/"

    def test_create(self):
        data = {
            "subject": self.subject.id,
            "academic_grade": self.grade.id,
            "weekly_hours": 5,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
