from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.core.tests.helpers import create_test_user
from apps.institutions.academic_grade.infrastructure.models import AcademicGrade
from apps.institutions.academic_level.infrastructure.models import AcademicLevel
from apps.institutions.school_year.infrastructure.models import SchoolYear
from apps.institutions.section.infrastructure.models import Section


class AcademicSublevelAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="sublevel@test.com", dni="4444444444",
            names="Sublevel", last_names="Tester", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.level = AcademicLevel.objects.create(name="Educacion Basica", code="EB")
        self.url = "/api/institutions/academic-sublevel/"
        self.payload = {
            "academic_level": self.level.id,
            "code": "EBM",
            "name": "Educacion Basica Media",
        }

    def test_list_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_sublevel(self):
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["name"], "Educacion Basica Media")

    def test_create_sublevel_with_description(self):
        payload = {**self.payload, "description": "Segundo ciclo"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["description"], "Segundo ciclo")

    def test_create_sublevel_empty_name_returns_422(self):
        payload = {**self.payload, "name": "", "code": "X"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_create_sublevel_empty_code_returns_422(self):
        payload = {**self.payload, "code": ""}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_get_sublevel(self):
        sublevel = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.get(f"{self.url}{sublevel['id']}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Educacion Basica Media")

    def test_get_sublevel_not_found(self):
        response = self.client.get(f"{self.url}99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_sublevel(self):
        sublevel = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.patch(
            f"{self.url}{sublevel['id']}/",
            {"name": "Educacion Basica Superior"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Educacion Basica Superior")

    def test_list_with_data(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

    def test_response_has_academic_level_name(self):
        sublevel = self.client.post(self.url, self.payload, format="json").data["data"]
        self.assertIn("academic_level_name", sublevel)
        self.assertEqual(sublevel["academic_level_name"], "Educacion Basica")

    def test_filter_by_academic_level(self):
        sublevel = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.get(self.url, {"academic_level": self.level.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)
        self.assertEqual(response.data["results"][0]["id"], sublevel["id"])

    def test_filter_by_is_active(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url, {"is_active": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_search_by_name(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url, {"search": "Media"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_search_by_code(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url, {"search": "EBM"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_soft_delete_without_children(self):
        sublevel = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.post(
            f"{self.url}{sublevel['id']}/soft-delete/", {"confirm": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["data"]["is_active"])
        self.assertIn("deactivated_records", response.data["data"])

    def test_soft_delete_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(f"{self.url}1/soft-delete/", format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AcademicSublevelCascadeTest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="cascade_sub@test.com", dni="3333333333",
            names="Cascade", last_names="Sub", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/institutions/academic-sublevel/"

        level = AcademicLevel.objects.create(name="Bachillerato", code="BCH")
        sublevel = self.client.post(
            self.url,
            {"academic_level": level.id, "code": "BCH-G", "name": "Bachillerato General"},
            format="json",
        ).data["data"]

        grade = AcademicGrade.objects.create(
            name="Primero Bachillerato", code="1BCH",
            academic_sublevel_id=sublevel["id"],
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

        self.sublevel_id = sublevel["id"]

    def test_soft_delete_with_children_requires_confirmation(self):
        response = self.client.post(
            f"{self.url}{self.sublevel_id}/soft-delete/", {"confirm": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["data"]["requires_confirmation"])
        self.assertTrue(response.data["data"]["is_active"])
        self.assertGreater(response.data["data"]["affected_records"], 0)

    def test_soft_delete_with_children_and_confirm_deactivates_cascade(self):
        response = self.client.post(
            f"{self.url}{self.sublevel_id}/soft-delete/", {"confirm": True}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("data", {})
        self.assertFalse(data.get("is_active"))
        self.assertGreater(data.get("deactivated_records"), 0)

    def test_soft_delete_cascade_deactivates_grades(self):
        self.client.post(
            f"{self.url}{self.sublevel_id}/soft-delete/", {"confirm": True}, format="json"
        )
        grades = AcademicGrade.objects.filter(academic_sublevel_id=self.sublevel_id)
        self.assertTrue(all(not g.is_active for g in grades))

    def test_soft_delete_cascade_deactivates_sections(self):
        self.client.post(
            f"{self.url}{self.sublevel_id}/soft-delete/", {"confirm": True}, format="json"
        )
        grade_ids = AcademicGrade.objects.filter(
            academic_sublevel_id=self.sublevel_id
        ).values_list("id", flat=True)
        sections = Section.objects.filter(academic_grade_id__in=grade_ids)
        self.assertTrue(all(not s.is_active for s in sections))


class AcademicSublevelPermissionTest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="noperm_sub@test.com", dni="2222222222",
            names="No", last_names="Perm", is_superuser=False,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/institutions/academic-sublevel/"

    def test_list_returns_403_without_permission(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_returns_403_without_permission(self):
        response = self.client.post(self.url, {"name": "Test", "code": "T"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
