from django.test import TestCase
from datetime import date
from decimal import Decimal
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear
from apps.institutions.models import Section
from apps.academic.academic_period import AcademicPeriod
from apps.academic.period_type import PeriodType
from apps.core.tests.helpers import create_test_student
from apps.students.models import Student
from apps.analytics.student_risk.infrastructure.models import StudentRiskScore, StudentFeatureSnapshot
from apps.analytics.services import AnalyticsService


class AnalyticsServiceTest(TestCase):
    """Tests para AnalyticsService"""

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
        self.period2 = AcademicPeriod.objects.create(
            school_year=self.school_year,
            name="Periodo 2",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 4, 30),
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
        self.student2 = create_test_student(
            document_number="0987654321",
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
        self.enrollment2 = Enrollment.objects.create(
            student=self.student2,
            section=self.section,
            enrollment_status="ACT",
        )

    def _create_risk(self, student, period, score, label):
        from apps.students.models import Enrollment
        enrollment = Enrollment.objects.filter(student=student, section__school_year=period.school_year).first()
        return StudentRiskScore.objects.create(
            enrollment=enrollment,
            academic_period=period,
            risk_score=score,
            risk_label=label,
            model_version="v1.0",
        )

    def _create_snapshot(self, student, period):
        from apps.students.models import Enrollment
        enrollment = Enrollment.objects.filter(student=student, section__school_year=period.school_year).first()
        return StudentFeatureSnapshot.objects.create(
            enrollment=enrollment,
            academic_period=period,
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
        self._create_risk(self.student, self.period2, Decimal("30.00"), "Bajo")

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
