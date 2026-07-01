from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.core.tests.helpers import create_test_user
from apps.institutions.academic_level.infrastructure.models import AcademicLevel
from apps.institutions.academic_sublevel.infrastructure.models import AcademicSublevel
from apps.institutions.school_year.infrastructure.models import SchoolYear
from apps.institutions.section.infrastructure.models import Section


class AcademicGradeAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="grade@test.com", dni="9999999999",
            names="Grade", last_names="Tester", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/institutions/academic-grades/"

        self.level = AcademicLevel.objects.create(name="Educacion Basica", code="EB")
        self.sublevel = AcademicSublevel.objects.create(
            academic_level=self.level, code="EBM", name="Educacion Basica Media"
        )
        self.payload = {
            "name": "Sexto Grado",
            "code": "6TO",
            "academic_sublevel": self.sublevel.id,
        }

    def test_list_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_grade(self):
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["name"], "Sexto Grado")

    def test_create_grade_without_sublevel_returns_422(self):
        payload = {"name": "Septimo Grado", "code": "7MO"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_create_grade_empty_name_returns_422(self):
        payload = {"name": "", "code": "X"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_create_grade_missing_name_returns_422(self):
        payload = {"code": "X"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_get_grade(self):
        grade = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.get(f"{self.url}{grade['id']}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Sexto Grado")

    def test_get_grade_not_found(self):
        response = self.client.get(f"{self.url}99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_grade(self):
        grade = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.patch(
            f"{self.url}{grade['id']}/",
            {"name": "Septimo Grado"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Septimo Grado")

    def test_list_with_data(self):
        post_resp = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(post_resp.status_code, status.HTTP_201_CREATED)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

    def test_response_has_academic_sublevel_name(self):
        grade = self.client.post(self.url, self.payload, format="json").data["data"]
        self.assertIn("academic_sublevel_name", grade)
        self.assertEqual(grade["academic_sublevel_name"], "Educacion Basica Media")

    def test_filter_by_sublevel(self):
        post_resp = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(post_resp.status_code, status.HTTP_201_CREATED)
        grade_id = post_resp.data["data"]["id"]
        response = self.client.get(
            self.url, {"academic_sublevel": self.sublevel.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertGreater(len(response.data["results"]), 0)
        self.assertEqual(response.data["results"][0]["id"], grade_id)

    def test_filter_by_is_active(self):
        post_resp = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(post_resp.status_code, status.HTTP_201_CREATED)
        response = self.client.get(self.url, {"is_active": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertGreater(len(response.data["results"]), 0)

    def test_search_by_name(self):
        post_resp = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(post_resp.status_code, status.HTTP_201_CREATED)
        response = self.client.get(self.url, {"search": "Sexto"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertGreater(len(response.data["results"]), 0)

    def test_soft_delete_without_children(self):
        grade = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.post(
            f"{self.url}{grade['id']}/soft-delete/", {"confirm": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["data"]["is_active"])
        self.assertIn("deactivated_records", response.data["data"])

    def test_soft_delete_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(f"{self.url}1/soft-delete/", format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AcademicGradeCascadeTest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="cascade@test.com", dni="8888888888",
            names="Cascade", last_names="Tester", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/institutions/academic-grades/"

        level = AcademicLevel.objects.create(name="Bachillerato", code="BACH")
        sublevel = AcademicSublevel.objects.create(
            academic_level=level, code="BACH", name="Bachillerato"
        )
        self.grade = self.client.post(
            self.url,
            {"name": "Primero Bachillerato", "code": "1BACH", "academic_sublevel": sublevel.id},
            format="json",
        ).data["data"]

        school_year = SchoolYear.objects.create(
            start_date=date(2024, 9, 1), end_date=date(2025, 6, 30)
        )
        section = Section.objects.create(
            school_year=school_year,
            academic_grade_id=self.grade["id"],
            parallel="A",
            capacity=30,
        )
        subject = Subject.objects.create(name="Matematicas", code="MAT-1BACH")
        config = SubjectAcademicConfig.objects.create(
            academic_grade_id=self.grade["id"],
            subject=subject,
            weekly_hours=5,
        )
        SubjectOffering.objects.create(
            section=section,
            subject_academic_config=config,
        )

    def test_soft_delete_with_children_requires_confirmation(self):
        grade_id = self.grade["id"]
        response = self.client.post(
            f"{self.url}{grade_id}/soft-delete/", {"confirm": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["data"]["requires_confirmation"])
        self.assertTrue(response.data["data"]["is_active"])
        self.assertGreater(response.data["data"]["affected_records"], 0)

    def test_soft_delete_with_children_and_confirm_deactivates_cascade(self):
        grade_id = self.grade["id"]
        response = self.client.post(
            f"{self.url}{grade_id}/soft-delete/", {"confirm": True}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("data", {})
        self.assertFalse(data.get("is_active"))
        self.assertGreater(data.get("deactivated_records"), 0)

        grade_resp = self.client.get(f"{self.url}{grade_id}/")
        grade = grade_resp.data.get("data", {})
        self.assertFalse(grade.get("is_active"))

    def test_soft_delete_cascade_deactivates_sections(self):
        grade_id = self.grade["id"]
        self.client.post(
            f"{self.url}{grade_id}/soft-delete/", {"confirm": True}, format="json"
        )
        sections = Section.objects.filter(academic_grade_id=grade_id)
        self.assertTrue(all(not s.is_active for s in sections))

    def test_soft_delete_cascade_deactivates_subject_offerings(self):
        grade_id = self.grade["id"]
        self.client.post(
            f"{self.url}{grade_id}/soft-delete/", {"confirm": True}, format="json"
        )
        section_ids = Section.objects.filter(academic_grade_id=grade_id).values_list("id", flat=True)
        offerings = SubjectOffering.objects.filter(section_id__in=section_ids)
        self.assertTrue(all(not o.is_active for o in offerings))

    def test_soft_delete_cascade_deactivates_subject_configs(self):
        grade_id = self.grade["id"]
        self.client.post(
            f"{self.url}{grade_id}/soft-delete/", {"confirm": True}, format="json"
        )
        configs = SubjectAcademicConfig.objects.filter(academic_grade_id=grade_id)
        self.assertTrue(all(not c.is_active for c in configs))


class AcademicGradePermissionTest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="noperm@test.com", dni="7777777777",
            names="No", last_names="Perm", is_superuser=False,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/institutions/academic-grades/"

    def test_list_returns_403_without_permission(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_returns_403_without_permission(self):
        response = self.client.post(self.url, {"name": "Test"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
