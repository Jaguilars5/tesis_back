from datetime import date, timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.core.tests.helpers import create_test_user
from apps.institutions.academic_grade.infrastructure.models import AcademicGrade
from apps.institutions.academic_level.infrastructure.models import AcademicLevel
from apps.institutions.academic_sublevel.infrastructure.models import AcademicSublevel
from apps.institutions.school_year.infrastructure.models import SchoolYear


class SectionAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="section@test.com", dni="5555555555",
            names="Section", last_names="Tester", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.school_year = SchoolYear.objects.create(
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=366),
        )
        level = AcademicLevel.objects.create(name="Basica", code="BAS")
        sublevel = AcademicSublevel.objects.create(
            academic_level=level, code="BAS-M", name="Basica Media"
        )
        self.grade = AcademicGrade.objects.create(
            name="Sexto", code="6TO", academic_sublevel=sublevel
        )
        self.url = "/api/institutions/section/"
        self.payload = {
            "school_year": self.school_year.id,
            "academic_grade": self.grade.id,
            "parallel": "A",
            "capacity": 30,
            "code": "SEC-A",
        }

    def test_list_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_section(self):
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["parallel"], "A")

    def test_create_section_with_code(self):
        payload = {**self.payload, "code": "SEC-A"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["code"], "SEC-A")

    def test_create_section_empty_parallel_returns_422(self):
        payload = {**self.payload, "parallel": ""}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_get_section(self):
        section = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.get(f"{self.url}{section['id']}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["parallel"], "A")

    def test_get_section_not_found(self):
        response = self.client.get(f"{self.url}99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_section(self):
        section = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.patch(
            f"{self.url}{section['id']}/",
            {"parallel": "B"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["parallel"], "B")

    def test_list_with_data(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

    def test_response_has_school_year_name(self):
        section = self.client.post(self.url, self.payload, format="json").data["data"]
        self.assertIn("school_year_name", section)
        self.assertIn("academic_grade_name", section)
        self.assertEqual(section["academic_grade_name"], "Sexto")

    def test_filter_by_school_year(self):
        section = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.get(self.url, {"school_year": self.school_year.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)
        self.assertEqual(response.data["results"][0]["id"], section["id"])

    def test_filter_by_academic_grade(self):
        section = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.get(self.url, {"academic_grade": self.grade.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)
        self.assertEqual(response.data["results"][0]["id"], section["id"])

    def test_filter_by_is_active(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url, {"is_active": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_search_by_parallel(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url, {"search": "A"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_soft_delete_without_children(self):
        section = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.post(
            f"{self.url}{section['id']}/soft-delete/", {"confirm": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["data"]["is_active"])
        self.assertIn("deactivated_records", response.data["data"])

    def test_soft_delete_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(f"{self.url}1/soft-delete/", format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy(self):
        section = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.delete(f"{self.url}{section['id']}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SectionCascadeTest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="sec_cascade@test.com", dni="4444444444",
            names="Sec", last_names="Cascade", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)

        school_year = SchoolYear.objects.create(
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=366),
        )
        level = AcademicLevel.objects.create(name="Bachillerato", code="BCH")
        sublevel = AcademicSublevel.objects.create(
            academic_level=level, code="BCH-G", name="Bachillerato General"
        )
        grade = AcademicGrade.objects.create(
            name="Primero", code="1BCH", academic_sublevel=sublevel
        )

        self.url = "/api/institutions/section/"
        resp = self.client.post(
            self.url,
            {
                "school_year": school_year.id,
                "academic_grade": grade.id,
                "parallel": "A",
                "capacity": 30,
                "code": "SEC-A",
            },
            format="json",
        )
        self.section_id = resp.data["data"]["id"]

        subject = Subject.objects.create(name="Matematicas", code="MAT-1BCH")
        config = SubjectAcademicConfig.objects.create(
            academic_grade=grade, subject=subject, weekly_hours=5
        )
        SubjectOffering.objects.create(
            section_id=self.section_id, subject_academic_config=config
        )

    def test_soft_delete_with_children_requires_confirmation(self):
        response = self.client.post(
            f"{self.url}{self.section_id}/soft-delete/", {"confirm": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["data"]["requires_confirmation"])
        self.assertTrue(response.data["data"]["is_active"])
        self.assertGreater(response.data["data"]["affected_records"], 0)

    def test_soft_delete_with_confirm_deactivates_cascade(self):
        response = self.client.post(
            f"{self.url}{self.section_id}/soft-delete/", {"confirm": True}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("data", {})
        self.assertFalse(data.get("is_active"))
        self.assertGreater(data.get("deactivated_records"), 0)

    def test_soft_delete_cascade_deactivates_offerings(self):
        self.client.post(
            f"{self.url}{self.section_id}/soft-delete/", {"confirm": True}, format="json"
        )
        offerings = SubjectOffering.objects.filter(section_id=self.section_id)
        self.assertTrue(all(not o.is_active for o in offerings))


class SectionPermissionTest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="noperm_sec@test.com", dni="6666666666",
            names="No", last_names="Perm", is_superuser=False,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/institutions/section/"

    def test_list_returns_403_without_permission(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_returns_403_without_permission(self):
        response = self.client.post(
            self.url, {"parallel": "A"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
