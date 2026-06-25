from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date

from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.institutions.academic_grade.infrastructure.models import AcademicGrade
from apps.institutions.academic_level.infrastructure.models import AcademicLevel
from apps.institutions.academic_sublevel.infrastructure.models import AcademicSublevel
from apps.institutions.school_year.infrastructure.models import SchoolYear
from apps.institutions.section.infrastructure.models import Section
from apps.core.tests.helpers import create_test_user

from ..infrastructure.models import SubjectOffering


class SubjectOfferingAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="offering@test.com", dni="4444444444",
            names="Offering", last_names="Tester", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        level = AcademicLevel.objects.create(name="Primaria")
        sublevel = AcademicSublevel.objects.create(academic_level=level, name="B\u00e1sica")
        grade = AcademicGrade.objects.create(academic_sublevel=sublevel, name="6to")
        school_year = SchoolYear.objects.create(start_date=date(2024, 9, 1), end_date=date(2025, 7, 31))
        self.section = Section.objects.create(school_year=school_year, academic_grade=grade, parallel="A", capacity=40)
        subject = Subject.objects.create(name="Matem\u00e1ticas", code="MAT-001")
        self.config = SubjectAcademicConfig.objects.create(subject=subject, academic_grade=grade, weekly_hours=5)
        self.url = "/api/academic/subject-offerings/"

    def test_list_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_create(self):
        data = {"section": self.section.id, "subject_academic_config": self.config.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])

    def test_retrieve(self):
        obj = SubjectOffering.objects.create(section=self.section, subject_academic_config=self.config)
        response = self.client.get(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])

    def test_update(self):
        obj = SubjectOffering.objects.create(section=self.section, subject_academic_config=self.config)
        data = {"section": self.section.id, "subject_academic_config": self.config.id}
        response = self.client.put(f"{self.url}{obj.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])

    def test_destroy(self):
        obj = SubjectOffering.objects.create(section=self.section, subject_academic_config=self.config)
        response = self.client.delete(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])

    def test_soft_delete(self):
        obj = SubjectOffering.objects.create(section=self.section, subject_academic_config=self.config)
        response = self.client.post(f"{self.url}{obj.id}/soft-delete/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertFalse(response.data["data"]["is_active"])

    def test_permission_denied(self):
        user_no_perm = create_test_user(
            email="noperm@test.com", dni="5555555555",
            names="No", last_names="Perm", is_superuser=False,
        )
        self.client.force_authenticate(user=user_no_perm)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_duplicate(self):
        SubjectOffering.objects.create(section=self.section, subject_academic_config=self.config)
        data = {"section": self.section.id, "subject_academic_config": self.config.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
