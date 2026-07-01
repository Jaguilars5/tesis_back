from datetime import date, timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.academic_period.infrastructure.models import AcademicPeriod
from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.core.tests.helpers import create_test_user
from apps.institutions.academic_grade.infrastructure.models import AcademicGrade
from apps.institutions.academic_level.infrastructure.models import AcademicLevel
from apps.academic.period_type.infrastructure.models import PeriodType
from apps.institutions.academic_sublevel.infrastructure.models import AcademicSublevel
from apps.institutions.section.infrastructure.models import Section


class SchoolYearAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="sy@test.com", dni="1111111111",
            names="School", last_names="Year", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/institutions/school-year/"
        self.tomorrow = date.today() + timedelta(days=1)
        self.next_year = date.today() + timedelta(days=366)
        self.payload = {
            "start_date": self.tomorrow.isoformat(),
            "end_date": self.next_year.isoformat(),
        }

    def test_list_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_school_year(self):
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])
        self.assertIn("id", response.data["data"])

    def test_create_school_year_past_start_date_returns_422(self):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        payload = {"start_date": yesterday, "end_date": self.next_year.isoformat()}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_create_school_year_end_before_start_returns_422(self):
        payload = {"start_date": self.next_year.isoformat(), "end_date": self.tomorrow.isoformat()}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_create_school_year_overlap_returns_422(self):
        self.client.post(self.url, self.payload, format="json")
        overlap = {
            "start_date": (self.tomorrow + timedelta(days=1)).isoformat(),
            "end_date": (self.next_year - timedelta(days=1)).isoformat(),
        }
        response = self.client.post(self.url, overlap, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_get_school_year(self):
        sy = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.get(f"{self.url}{sy['id']}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["id"], sy["id"])

    def test_get_school_year_not_found(self):
        response = self.client.get(f"{self.url}99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_school_year(self):
        sy = self.client.post(self.url, self.payload, format="json").data["data"]
        later = (self.tomorrow + timedelta(days=10)).isoformat()
        response = self.client.patch(
            f"{self.url}{sy['id']}/",
            {"start_date": later},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_with_data(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertGreater(len(response.data["results"]), 0)

    def test_filter_by_is_active(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url, {"is_active": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_filter_by_start_date_gte(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.get(self.url, {"start_date__gte": self.tomorrow.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_soft_delete_without_children(self):
        sy = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.post(
            f"{self.url}{sy['id']}/soft-delete/", {"confirm": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["data"]["is_active"])

    def test_soft_delete_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(f"{self.url}1/soft-delete/", format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy(self):
        sy = self.client.post(self.url, self.payload, format="json").data["data"]
        response = self.client.delete(f"{self.url}{sy['id']}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SchoolYearCascadeTest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="sy_cascade@test.com", dni="2222222222",
            names="SY", last_names="Cascade", is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/institutions/school-year/"

        tomorrow = date.today() + timedelta(days=1)
        next_year = date.today() + timedelta(days=366)

        sy_resp = self.client.post(
            self.url,
            {"start_date": tomorrow.isoformat(), "end_date": next_year.isoformat()},
            format="json",
        )
        self.sy_id = sy_resp.data["data"]["id"]

        level = AcademicLevel.objects.create(name="Basica", code="BAS")
        sublevel = AcademicSublevel.objects.create(
            academic_level=level, code="BAS-M", name="Basica Media"
        )
        grade = AcademicGrade.objects.create(
            name="Sexto", code="6TO", academic_sublevel=sublevel
        )
        section = Section.objects.create(
            school_year_id=self.sy_id, academic_grade=grade,
            parallel="A", capacity=30,
        )
        subject = Subject.objects.create(name="Mate", code="MAT-6")
        config = SubjectAcademicConfig.objects.create(
            academic_grade=grade, subject=subject, weekly_hours=5
        )
        SubjectOffering.objects.create(section=section, subject_academic_config=config)
        period_type = PeriodType.objects.create(code="TRI", name="Trimestre", divisions_per_year=3)
        AcademicPeriod.objects.create(
            school_year_id=self.sy_id, period_type=period_type,
            name="Trimestre 1", start_date=tomorrow,
            end_date=next_year, year_weight=30,
        )

    def test_soft_delete_with_children_requires_confirmation(self):
        response = self.client.post(
            f"{self.url}{self.sy_id}/soft-delete/", {"confirm": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["data"]["requires_confirmation"])
        self.assertTrue(response.data["data"]["is_active"])
        self.assertGreater(response.data["data"]["affected_records"], 0)

    def test_soft_delete_with_confirm_deactivates_cascade(self):
        response = self.client.post(
            f"{self.url}{self.sy_id}/soft-delete/", {"confirm": True}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("data", {})
        self.assertFalse(data.get("is_active"))
        self.assertGreater(data.get("deactivated_records"), 0)

    def test_soft_delete_cascade_deactivates_sections(self):
        self.client.post(
            f"{self.url}{self.sy_id}/soft-delete/", {"confirm": True}, format="json"
        )
        sections = Section.objects.filter(school_year_id=self.sy_id)
        self.assertTrue(all(not s.is_active for s in sections))

    def test_soft_delete_cascade_deactivates_academic_periods(self):
        self.client.post(
            f"{self.url}{self.sy_id}/soft-delete/", {"confirm": True}, format="json"
        )
        periods = AcademicPeriod.objects.filter(school_year_id=self.sy_id)
        self.assertTrue(all(not p.is_active for p in periods))


class SchoolYearPermissionTest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="noperm_sy@test.com", dni="3333333333",
            names="No", last_names="Perm", is_superuser=False,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/institutions/school-year/"

    def test_list_returns_403_without_permission(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_returns_403_without_permission(self):
        response = self.client.post(
            self.url,
            {"start_date": "2026-01-01", "end_date": "2026-12-31"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
