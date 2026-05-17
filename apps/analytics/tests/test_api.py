from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from decimal import Decimal
from apps.institutions.models import AcademicGrade, AcademicLevel, Institution, School_Year
from apps.academic.models import Config_Academic, Academic_Period, Timing_Regime, Section
from apps.students.models import Student
from apps.accounts.models import Role, User
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.analytics.models import RiskFactor, StudentFeatureSnapshot, StudentRiskScore


class StudentRiskAPITest(APITestCase):
    """Tests para endpoints de StudentRiskScore"""

    def setUp(self):
        self.institution = Institution.objects.create(
            name="Test School", code="TS-001", address="Test St", city="Quito"
        )
        self.school_year = School_Year.objects.create(
            institution=self.institution,
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.config = Config_Academic.objects.create(
            school_year=self.school_year,
            institution=self.institution,
            name="Config 2024",
            academic_period_type="Trimestral",
            number_of_periods=3,
        )
        self.period = Academic_Period.objects.create(
            config_academic=self.config,
            name="Periodo 1",

            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 15),
        )
        self.timing = Timing_Regime.objects.create(
            institution=self.institution, name="Matutina"
        )
        self.academic_level = AcademicLevel.objects.create(
            institution=self.institution, name="Primaria"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level, name="6to", sequence_order=6
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            timing_regime=self.timing,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=40,
        )
        self.student = create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Perez",
            birth_date=date(2012, 5, 15),
        )
        self.risk = StudentRiskScore.objects.create(
            student=self.student,
            academic_period=self.period,
            risk_score=Decimal("75.50"),
            risk_label="Alto",
            model_version="v1.0",
        )

        role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="test@test.com",
            dni="1717171717",
            names="Test",
            last_names="User",
            institution=self.institution,
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_list_risk_scores(self):
        response = self.client.get("/api/analytics/student-risk-scores/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertEqual(len(response.data["data"]["results"]), 1)

    def test_get_risk_score(self):
        response = self.client.get(
            f"/api/analytics/student-risk-scores/{self.risk.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["risk_label"], "Alto")

    def test_get_risk_score_not_found(self):
        response = self.client.get("/api/analytics/student-risk-scores/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["ok"])


class FeatureSnapshotAPITest(APITestCase):
    """Tests para endpoints de StudentFeatureSnapshot"""

    def setUp(self):
        self.institution = Institution.objects.create(
            name="Test School", code="TS-001", address="Test St", city="Quito"
        )
        self.school_year = School_Year.objects.create(
            institution=self.institution,
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.config = Config_Academic.objects.create(
            school_year=self.school_year,
            institution=self.institution,
            name="Config 2024",
            academic_period_type="Trimestral",
            number_of_periods=3,
        )
        self.period = Academic_Period.objects.create(
            config_academic=self.config,
            name="Periodo 1",

            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 15),
        )
        self.timing = Timing_Regime.objects.create(
            institution=self.institution, name="Matutina"
        )
        self.academic_level = AcademicLevel.objects.create(
            institution=self.institution, name="Primaria"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level, name="6to", sequence_order=6
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            timing_regime=self.timing,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=40,
        )
        self.student = create_test_student(
            document_number="1234567890",
            names="Maria",
            last_names="Lopez",
            birth_date=date(2012, 3, 10),
        )
        self.snapshot = StudentFeatureSnapshot.objects.create(
            student=self.student,
            academic_period=self.period,
            attendance_rate=Decimal("85.00"),
            consecutive_absences_max=3,
            tardiness_count=5,
            avg_grade_normalized=Decimal("7.50"),
            grade_trend_slope=Decimal("-0.10"),
            failing_subjects_count=2,
            conduct_score=Decimal("8.00"),
            family_notified_ratio=Decimal("0.30"),
            age_grade_gap=0,
        )

        role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="test@test.com",
            dni="1717171717",
            names="Test",
            last_names="User",
            institution=self.institution,
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_list_snapshots(self):
        response = self.client.get("/api/analytics/feature-snapshots/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertEqual(len(response.data["data"]["results"]), 1)

    def test_get_snapshot(self):
        response = self.client.get(
            f"/api/analytics/feature-snapshots/{self.snapshot.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["attendance_rate"], "85.00")

    def test_get_snapshot_not_found(self):
        response = self.client.get("/api/analytics/feature-snapshots/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["ok"])


class RiskFactorAPITest(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="riskfactor@test.com",
            dni="5050505050",
            names="RiskFactor",
            last_names="Tester",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        RiskFactor.objects.create(
            code="ASIST_BAJA",
            name="Asistencia Baja",
            description="Estudiante con alta tasa de inasistencia",
        )
        RiskFactor.objects.create(
            code="REND_DECL",
            name="Rendimiento Declinante",
        )
        self.url = "/api/analytics/risk-factors/"

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        obj = RiskFactor.objects.first()
        response = self.client.get(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_not_allowed(self):
        response = self.client.post(
            self.url,
            {"code": "COND_NEG", "name": "Conducta Negativa"},
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
