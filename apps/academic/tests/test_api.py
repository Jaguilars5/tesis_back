from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from decimal import Decimal
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear
from apps.institutions.models import Section
from apps.academic.models import AcademicPeriod, PeriodType, Subject
from apps.iam.models import Role, User
from apps.core.tests.helpers import create_test_user


class AcademicAPITest(APITestCase):
    """Tests para los endpoints API de Academic"""

    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, name="Básica"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel, name="6to"
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
        self.section_url = "/api/institutions/section/"

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


class AcademicPeriodAPIBusinessRulesTest(APITestCase):
    """Verifica que las reglas de negocio se apliquen en la API y devuelvan {ok:false}."""

    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.trimestre = PeriodType.objects.create(
            code="TRIMESTRE-API", name="Trimestre", divisions_per_year=3
        )
        self.bimestre = PeriodType.objects.create(
            code="BIMESTRE-API", name="Bimestre", divisions_per_year=4
        )
        self.user = create_test_user(
            email="api@test.com",
            dni="1818181818",
            names="API",
            last_names="Tester",
            password="test_password_123",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/academic/academic-period/"

    def _payload(self, **overrides):
        data = {
            "school_year": self.school_year.id,
            "name": "Q1",
            "period_type": self.trimestre.id,
            "start_date": "2025-01-01",
            "end_date": "2025-03-31",
        }
        data.update(overrides)
        return data

    def test_create_period_ok_returns_standard_format(self):
        response = self.client.post(self.url, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])
        self.assertIn("data", response.data)
        self.assertEqual(response.data["msg"], "Período académico creado")

    def test_exceeding_divisions_returns_400_with_validation_errors(self):
        for i, (s, e) in enumerate(
            [
                ("2025-01-01", "2025-03-31"),
                ("2025-04-01", "2025-06-30"),
                ("2025-07-01", "2025-09-30"),
            ],
            start=1,
        ):
            response = self.client.post(self.url, self._payload(name=f"Q{i}", start_date=s, end_date=e), format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        response = self.client.post(
            self.url,
            self._payload(name="Q4", start_date="2025-10-01", end_date="2025-11-30"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertFalse(response.data["ok"])
        self.assertIn("No se pueden crear mas periodos", response.data["msg"])
        self.assertIn("period_type", response.data["data"])
        self.assertIn("No se pueden crear mas periodos", response.data["data"]["period_type"])

    def test_mixing_period_types_returns_400_with_validation_errors(self):
        response = self.client.post(self.url, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            self.url,
            self._payload(
                name="S1",
                period_type=self.bimestre.id,
                start_date="2025-04-01",
                end_date="2025-05-31",
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("Estandar educativo Ecuador", response.data["msg"])
        self.assertIn("period_type", response.data["data"])
        self.assertIn("Estandar educativo Ecuador", response.data["data"]["period_type"])

    def test_dates_outside_school_year_returns_400(self):
        response = self.client.post(
            self.url,
            self._payload(start_date="2024-09-01", end_date="2024-12-31"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("dentro del rango del anio", response.data["msg"])
        self.assertIn("school_year", response.data["data"])
        self.assertIn("dentro del rango del anio", response.data["data"]["school_year"])

    def test_overlapping_periods_returns_400(self):
        response = self.client.post(
            self.url,
            self._payload(name="Q1", start_date="2025-01-01", end_date="2025-04-30"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            self.url,
            self._payload(name="Q1-bis", start_date="2025-03-01", end_date="2025-05-31"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("superpone", response.data["msg"])
        self.assertIn("start_date", response.data["data"])
        self.assertIn("superpone", response.data["data"]["start_date"])

    def test_year_weight_exceeds_100_returns_400(self):
        response = self.client.post(
            self.url,
            self._payload(name="Q1", start_date="2025-01-01", end_date="2025-03-31", year_weight="40.00"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(
            self.url,
            self._payload(name="Q2", start_date="2025-04-01", end_date="2025-06-30", year_weight="70.00"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("excede 100%", response.data["msg"])
        self.assertIn("year_weight", response.data["data"])
        self.assertIn("excede 100%", response.data["data"]["year_weight"])

    def test_update_period_validates_overlap_returns_400(self):
        period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.trimestre,
            name="Q1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.trimestre,
            name="Q2",
            start_date=date(2025, 4, 1),
            end_date=date(2025, 6, 30),
        )
        response = self.client.patch(
            f"{self.url}{period.id}/",
            {"end_date": "2025-05-15"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("superpone", response.data["msg"])
        self.assertIn("start_date", response.data["data"])
        self.assertIn("superpone", response.data["data"]["start_date"])

    def test_update_period_validates_school_year_range_returns_400(self):
        period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            period_type=self.trimestre,
            name="Q1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        response = self.client.patch(
            f"{self.url}{period.id}/",
            {"start_date": "2024-09-01", "end_date": "2024-12-31"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("dentro del rango del anio", response.data["msg"])
        self.assertIn("school_year", response.data["data"])
