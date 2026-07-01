from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.core.tests.helpers import create_test_user
from apps.institutions.academic_grade.infrastructure.models import AcademicGrade
from apps.institutions.academic_sublevel.infrastructure.models import AcademicSublevel
from apps.institutions.school_year.infrastructure.models import SchoolYear
from apps.institutions.section.infrastructure.models import Section


class AcademicLevelAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="level@test.com", dni="7777777777",
            names="Level", last_names="Tester", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/institutions/academic-levels/"
        self.payload = {"name": "Educacion Inicial", "code": "EI"}

    def test_list_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_level(self):
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["name"], "Educacion Inicial")
        self.assertIn("description", response.data["data"])

    def test_create_level_without_code_returns_422(self):
        payload = {"name": "Educacion Basica"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_create_level_with_description(self):
        payload = {"name": "Inicial", "code": "INI", "description": "Nivel inicial"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["description"], "Nivel inicial")

    def test_create_level_empty_name_returns_422(self):
        payload = {"name": "", "code": "X"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_create_level_missing_name_returns_422(self):
        payload = {"code": "X"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_get_level(self):
        level = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.get(f"{self.url}{level['id']}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Educacion Inicial")

    def test_get_level_not_found(self):
        response = self.client.get(f"{self.url}99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_level(self):
        level = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.patch(
            f"{self.url}{level['id']}/",
            {"name": "Educacion Basica"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Educacion Basica")

    def test_list_with_data(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_by_is_active(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url, {"is_active": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_filter_by_name_icontains(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url, {"name__icontains": "Inicial"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_search_by_name(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url, {"search": "Inicial"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_soft_delete_without_children(self):
        level = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.post(
            f"{self.url}{level['id']}/soft-delete/", {"confirm": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["data"]["is_active"])
        self.assertIn("deactivated_records", response.data["data"])

    def test_soft_delete_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(f"{self.url}1/soft-delete/", format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AcademicLevelCascadeTest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="cascade_lvl@test.com", dni="6666666666",
            names="Cascade", last_names="Level", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/institutions/academic-levels/"

        level = self.client.post(
            self.url, {"name": "Bachillerato", "code": "BCH"}, format="json"
        ).data["data"]

        sublevel = AcademicSublevel.objects.create(
            academic_level_id=level["id"], code="BCH-G", name="Bachillerato General"
        )
        grade = AcademicGrade.objects.create(
            name="Primero Bachillerato", code="1BCH", academic_sublevel=sublevel
        )
        school_year = SchoolYear.objects.create(
            start_date=date(2024, 9, 1), end_date=date(2025, 6, 30)
        )
        section = Section.objects.create(
            school_year=school_year, academic_grade=grade, parallel="A", capacity=30
        )
        subject = Subject.objects.create(name="Matematicas", code="MAT-BCH")
        config = SubjectAcademicConfig.objects.create(
            academic_grade=grade, subject=subject, weekly_hours=5
        )
        SubjectOffering.objects.create(section=section, subject_academic_config=config)

        self.level_id = level["id"]

    def test_soft_delete_with_children_requires_confirmation(self):
        response = self.client.post(
            f"{self.url}{self.level_id}/soft-delete/", {"confirm": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["data"]["requires_confirmation"])
        self.assertTrue(response.data["data"]["is_active"])
        self.assertGreater(response.data["data"]["affected_records"], 0)

    def test_soft_delete_with_children_and_confirm_deactivates_cascade(self):
        response = self.client.post(
            f"{self.url}{self.level_id}/soft-delete/", {"confirm": True}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("data", {})
        self.assertFalse(data.get("is_active"))
        self.assertGreater(data.get("deactivated_records"), 0)

    def test_soft_delete_cascade_deactivates_sublevels(self):
        self.client.post(
            f"{self.url}{self.level_id}/soft-delete/", {"confirm": True}, format="json"
        )
        sublevels = AcademicSublevel.objects.filter(academic_level_id=self.level_id)
        self.assertTrue(all(not s.is_active for s in sublevels))

    def test_soft_delete_cascade_deactivates_grades(self):
        self.client.post(
            f"{self.url}{self.level_id}/soft-delete/", {"confirm": True}, format="json"
        )
        sublevel_ids = AcademicSublevel.objects.filter(
            academic_level_id=self.level_id
        ).values_list("id", flat=True)
        grades = AcademicGrade.objects.filter(academic_sublevel_id__in=sublevel_ids)
        self.assertTrue(all(not g.is_active for g in grades))


class AcademicLevelPermissionTest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="noperm_lvl@test.com", dni="5555555555",
            names="No", last_names="Perm", is_superuser=False,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/institutions/academic-levels/"

    def test_list_returns_403_without_permission(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_returns_403_without_permission(self):
        response = self.client.post(self.url, {"name": "Test"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
