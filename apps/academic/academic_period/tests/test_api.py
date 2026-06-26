from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date

from apps.academic.period_type.infrastructure.models import PeriodType
from apps.institutions.school_year.infrastructure.models import SchoolYear
from apps.academic.academic_period.infrastructure.models import AcademicPeriod
from apps.core.tests.helpers import create_test_user


class AcademicPeriodAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="academic_period@test.com",
            dni="9999999999",
            names="AP",
            last_names="Tester",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.school_year = SchoolYear.objects.create(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )
        self.period_type_1 = PeriodType.objects.create(
            code="TRIM",
            name="Trimestre",
            divisions_per_year=3,
        )
        self.period_type_2 = PeriodType.objects.create(
            code="SEMESTRE",
            name="Semestre",
            divisions_per_year=2,
        )
        self.url = "/api/academic/academic-periods/"

    def test_list(self):
        AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type_1,
            name="Primer Trimestre",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            year_weight=30.0,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # La paginación en Django REST Framework no se procesa a nivel de response.data por renderers en APITestCase por defecto,
        # así que validamos directamente sobre el diccionario de resultados.
        self.assertEqual(len(response.data["results"]), 1)

    def test_create(self):
        data = {
            "school_year": self.school_year.id,
            "period_type": self.period_type_1.id,
            "name": "Segundo Trimestre",
            "start_date": "2026-05-01",
            "end_date": "2026-08-31",
            "year_weight": 35.0,
            "is_regular_period": True,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["name"], "Segundo Trimestre")

    def test_get(self):
        period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type_1,
            name="Primer Trimestre",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            year_weight=30.0,
        )
        response = self.client.get(f"{self.url}{period.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["name"], "Primer Trimestre")

    def test_update_period_type(self):
        period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type_1,
            name="Primer Trimestre",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            year_weight=30.0,
        )
        data = {
            "school_year": self.school_year.id,
            "period_type": self.period_type_2.id,
            "name": "Primer Semestre",
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "year_weight": 50.0,
            "is_regular_period": True,
        }
        response = self.client.put(f"{self.url}{period.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["name"], "Primer Semestre")
        self.assertEqual(response.data["data"]["period_type"], self.period_type_2.id)

        # Verificar en base de datos
        period.refresh_from_db()
        self.assertEqual(period.period_type, self.period_type_2)
        self.assertEqual(period.name, "Primer Semestre")

    def test_update_period_type_invalid(self):
        period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type_1,
            name="Primer Trimestre",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            year_weight=30.0,
        )
        data = {
            "school_year": self.school_year.id,
            "period_type": 9999,  # ID inexistente
            "name": "Primer Semestre",
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "year_weight": 50.0,
            "is_regular_period": True,
        }
        response = self.client.put(f"{self.url}{period.id}/", data, format="json")
        # El custom_exception_handler convierte ValidationError a HTTP 422
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_filter_by_school_year(self):
        # Create second school year
        school_year_2 = SchoolYear.objects.create(
            start_date=date(2027, 1, 1),
            end_date=date(2027, 12, 31),
        )
        # Create period in school_year 1
        AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type_1,
            name="Primer Trimestre 2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            year_weight=30.0,
        )
        # Create period in school_year 2
        AcademicPeriod.objects.create(
            school_year=school_year_2,
            period_type=self.period_type_1,
            name="Primer Trimestre 2027",
            start_date=date(2027, 1, 1),
            end_date=date(2027, 4, 30),
            year_weight=30.0,
        )
        # Filter by school_year 1
        response = self.client.get(f"{self.url}?school_year={self.school_year.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Primer Trimestre 2026")

    def test_search_by_name(self):
        AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type_1,
            name="Primer Trimestre",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            year_weight=30.0,
        )
        AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type_1,
            name="Segundo Trimestre",
            start_date=date(2026, 5, 1),
            end_date=date(2026, 8, 31),
            year_weight=30.0,
        )
        response = self.client.get(f"{self.url}?search=Segundo")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Segundo Trimestre")

    def test_ordering_by_start_date(self):
        # Earliest period
        p1 = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type_1,
            name="Primer Trimestre",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            year_weight=30.0,
        )
        # Later period
        p2 = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type_1,
            name="Segundo Trimestre",
            start_date=date(2026, 5, 1),
            end_date=date(2026, 8, 31),
            year_weight=30.0,
        )
        # Default ordering is -start_date (latest first)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["id"], p2.id)
        self.assertEqual(response.data["results"][1]["id"], p1.id)

        # Ordering by start_date (earliest first)
        response = self.client.get(f"{self.url}?ordering=start_date")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["id"], p1.id)
        self.assertEqual(response.data["results"][1]["id"], p2.id)

    def test_soft_delete_without_confirm(self):
        period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type_1,
            name="Primer Trimestre",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            year_weight=30.0,
        )
        response = self.client.post(f"{self.url}{period.id}/soft-delete/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        # Sin hijos en cascada: desactiva inmediatamente
        self.assertFalse(response.data["data"]["is_active"])

    def test_soft_delete_with_confirm(self):
        period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type_1,
            name="Primer Trimestre",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            year_weight=30.0,
        )
        response = self.client.post(
            f"{self.url}{period.id}/soft-delete/",
            {"confirm": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertFalse(response.data["data"]["is_active"])

    def test_destroy(self):
        period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type_1,
            name="Primer Trimestre",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            year_weight=30.0,
        )
        response = self.client.delete(f"{self.url}{period.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])

    def test_permission_denied(self):
        from apps.core.tests.helpers import create_test_user

        user_no_perm = create_test_user(
            email="noperm@test.com",
            dni="8888888888",
            names="No",
            last_names="Perm",
            is_superuser=False,
        )
        self.client.force_authenticate(user=user_no_perm)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_soft_delete_cascade_no_children(self):
        period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type_1,
            name="Primer Trimestre",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            year_weight=30.0,
        )
        response = self.client.post(
            f"{self.url}{period.id}/soft-delete/", {"confirm": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"].get("deactivated_records"), 0)

    def test_create_date_overlap_returns_422(self):
        AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.period_type_1,
            name="Primer Trimestre",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            year_weight=30.0,
        )
        data = {
            "school_year": self.school_year.id,
            "period_type": self.period_type_1.id,
            "name": "Segundo Trimestre",
            "start_date": "2026-03-01",
            "end_date": "2026-06-30",
            "year_weight": 35.0,
            "is_regular_period": True,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_create_validation_error(self):
        data = {
            "school_year": self.school_year.id,
            "period_type": self.period_type_1.id,
            "name": "",
            "start_date": "invalid-date",
            "end_date": "2026-08-31",
            "year_weight": 35.0,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

