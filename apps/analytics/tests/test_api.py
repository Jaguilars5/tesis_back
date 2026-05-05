from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from decimal import Decimal
from apps.institutions.models import Institution, School_Year
from apps.academic.models import Config_Academic, Academic_Period, Timing_Regime, Section
from apps.students.models import Student
from apps.accounts.models import Role, User
from apps.analytics.models import StudentRiskScore, StudentFeatureSnapshot


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
            number=1,
            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 15),
        )
        self.timing = Timing_Regime.objects.create(
            school_year=self.school_year, name="Matutina"
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            timing_regime=self.timing,
            level="Primaria",
            grade="6to",
            parallel="A",
            capacity=40,
        )
        self.student = Student.objects.create(
            dni="1234567890",
            names="Juan",
            last_names="Perez",
            birth_date=date(2012, 5, 15),
            section=self.section,
        )
        self.risk = StudentRiskScore.objects.create(
            student=self.student,
            academic_period=self.period,
            risk_score=Decimal("75.50"),
            risk_label="Alto",
            top_factors={"absences": 0.4},
            model_version="v1.0",
        )

        role = Role.objects.create(name="Admin")
        self.user = User.objects.create_user(
            email="test@test.com",
            dni="1717171717",
            names="Test",
            last_names="User",
            password="testpass123",
            role=role,
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
            number=1,
            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 15),
        )
        self.timing = Timing_Regime.objects.create(
            school_year=self.school_year, name="Matutina"
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            timing_regime=self.timing,
            level="Primaria",
            grade="6to",
            parallel="A",
            capacity=40,
        )
        self.student = Student.objects.create(
            dni="1234567890",
            names="Maria",
            last_names="Lopez",
            birth_date=date(2012, 3, 10),
            section=self.section,
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
        self.user = User.objects.create_user(
            email="test@test.com",
            dni="1717171717",
            names="Test",
            last_names="User",
            password="testpass123",
            role=role,
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
