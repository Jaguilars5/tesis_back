from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from decimal import Decimal
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear
from apps.institutions.models import Section
from apps.academic.models import AcademicPeriod, PeriodType
from apps.students.models import Student
from apps.iam.models import Role, User
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.analytics.models import RiskFactor, StudentFeatureSnapshot, StudentRiskScore


class StudentRiskAPITest(APITestCase):
    """Tests para endpoints de StudentRiskScore"""

    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            name="Periodo 1",
            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 15),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, name="Básica"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel, name="6to"
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
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
        from apps.students.models import Enrollment
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            section=self.section,
            enrollment_status="ACT",
        )
        self.risk = StudentRiskScore.objects.create(
            enrollment=self.enrollment,
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
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_list_risk_scores(self):
        response = self.client.get("/api/analytics/student-risk-scores/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(len(response.json()["data"]["results"]), 1)

    def test_get_risk_score(self):
        response = self.client.get(
            f"/api/analytics/student-risk-scores/{self.risk.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(response.json()["data"]["risk_label"], "Alto")

    def test_get_risk_score_not_found(self):
        response = self.client.get("/api/analytics/student-risk-scores/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.json()["ok"])


class FeatureSnapshotAPITest(APITestCase):
    """Tests para endpoints de StudentFeatureSnapshot"""

    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            name="Periodo 1",
            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 15),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, name="Básica"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel, name="6to"
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
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
        from apps.students.models import Enrollment
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            section=self.section,
            enrollment_status="ACT",
        )
        self.snapshot = StudentFeatureSnapshot.objects.create(
            enrollment=self.enrollment,
            academic_period=self.period,
            attendance_rate=Decimal("85.00"),
            consecutive_absences_max=3,
            tardiness_count=5,
            formative_avg_normalized=Decimal("7.50"),
            summative_avg_normalized=Decimal("7.50"),
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
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_list_snapshots(self):
        response = self.client.get("/api/analytics/feature-snapshots/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(len(response.json()["data"]["results"]), 1)

    def test_get_snapshot(self):
        response = self.client.get(
            f"/api/analytics/feature-snapshots/{self.snapshot.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(response.json()["data"]["attendance_rate"], "85.00")

    def test_get_snapshot_not_found(self):
        response = self.client.get("/api/analytics/feature-snapshots/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.json()["ok"])


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
