from django.test import TestCase
from datetime import date
from decimal import Decimal
from apps.institutions.models import Institution, School_Year
from apps.academic.models import Config_Academic, Academic_Period, Timing_Regime, Section
from apps.students.models import Student
from apps.analytics.models import StudentRiskScore, StudentFeatureSnapshot
from apps.analytics.services import AnalyticsService


class AnalyticsServiceTest(TestCase):
    """Tests para AnalyticsService"""

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
        self.student2 = Student.objects.create(
            dni="0987654321",
            names="Maria",
            last_names="Lopez",
            birth_date=date(2012, 3, 10),
            section=self.section,
        )

    def _create_risk(self, student, period, score, label):
        return StudentRiskScore.objects.create(
            student=student,
            academic_period=period,
            risk_score=score,
            risk_label=label,
            top_factors={"test": True},
            model_version="v1.0",
        )

    def _create_snapshot(self, student, period):
        return StudentFeatureSnapshot.objects.create(
            student=student,
            academic_period=period,
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

    def test_get_student_risk_profile_with_data(self):
        risk = self._create_risk(self.student, self.period, Decimal("75.00"), "Alto")
        snapshot = self._create_snapshot(self.student, self.period)

        profile = AnalyticsService.get_student_risk_profile(self.student.id)
        self.assertEqual(profile["risk_score"].pk, risk.pk)
        self.assertEqual(profile["metrics_snapshot"].pk, snapshot.pk)

    def test_get_student_risk_profile_no_data(self):
        profile = AnalyticsService.get_student_risk_profile(99999)
        self.assertIsNone(profile["risk_score"])
        self.assertIsNone(profile["metrics_snapshot"])

    def test_get_student_risk_profile_no_snapshot(self):
        self._create_risk(self.student, self.period, Decimal("50.00"), "Medio")

        profile = AnalyticsService.get_student_risk_profile(self.student.id)
        self.assertIsNotNone(profile["risk_score"])
        self.assertIsNone(profile["metrics_snapshot"])

    def test_list_priority_students(self):
        self._create_risk(self.student, self.period, Decimal("85.00"), "Alto")
        self._create_risk(self.student2, self.period, Decimal("72.00"), "Alto")
        self._create_risk(self.student, self.period, Decimal("30.00"), "Bajo")

        high_risk = AnalyticsService.list_priority_students(self.period.id)
        self.assertEqual(high_risk.count(), 2)

    def test_list_priority_students_empty(self):
        high_risk = AnalyticsService.list_priority_students(self.period.id)
        self.assertEqual(high_risk.count(), 0)

    def test_list_priority_students_custom_threshold(self):
        self._create_risk(self.student, self.period, Decimal("60.00"), "Medio")
        self._create_risk(self.student2, self.period, Decimal("90.00"), "Alto")

        high_risk = AnalyticsService.list_priority_students(self.period.id)
        self.assertEqual(high_risk.count(), 1)
        self.assertEqual(high_risk.first().risk_score, Decimal("90.00"))
