from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date

from apps.academic.subject.infrastructure.models import Subject
from apps.institutions.academic_grade.infrastructure.models import AcademicGrade
from apps.institutions.academic_level.infrastructure.models import AcademicLevel
from apps.institutions.academic_sublevel.infrastructure.models import AcademicSublevel
from apps.core.tests.helpers import create_test_user

from ..infrastructure.models import SubjectAcademicConfig


class SubjectAcademicConfigAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="config@test.com",
            dni="3333333333",
            names="Config",
            last_names="Tester",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        level = AcademicLevel.objects.create(name="Primaria")
        sublevel = AcademicSublevel.objects.create(academic_level=level, name="Basica")
        self.grade = AcademicGrade.objects.create(
            academic_sublevel=sublevel, name="6to"
        )
        self.subject = Subject.objects.create(name="Matematicas", code="MAT-001")
        self.url = "/api/academic/subject-academic-configs/"

    def test_list_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_create(self):
        data = {
            "subject": self.subject.id,
            "academic_grade": self.grade.id,
            "weekly_hours": 5,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])

    def test_retrieve(self):
        obj = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=5,
        )
        response = self.client.get(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["weekly_hours"], 5)

    def test_update(self):
        obj = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=5,
        )
        data = {
            "weekly_hours": 6,
            "subject": self.subject.id,
            "academic_grade": self.grade.id,
        }
        response = self.client.put(f"{self.url}{obj.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["weekly_hours"], 6)

    def test_destroy(self):
        obj = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=5,
        )
        response = self.client.delete(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])

    def test_soft_delete(self):
        obj = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=5,
        )
        response = self.client.post(f"{self.url}{obj.id}/soft-delete/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertFalse(response.data["data"]["is_active"])

    def test_permission_denied(self):
        user_no_perm = create_test_user(
            email="noperm@test.com",
            dni="4444444444",
            names="No",
            last_names="Perm",
            is_superuser=False,
        )
        self.client.force_authenticate(user=user_no_perm)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_duplicate(self):
        SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.grade,
            weekly_hours=5,
        )
        data = {
            "subject": self.subject.id,
            "academic_grade": self.grade.id,
            "weekly_hours": 6,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
