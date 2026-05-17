from django.test import TestCase
from datetime import date
from decimal import Decimal
from apps.institutions.models import AcademicGrade, AcademicLevel, Institution, School_Year
from apps.academic.models import Config_Academic, Academic_Period, Timing_Regime, Section
from apps.core.tests.helpers import create_test_student
from apps.students.models import Student
from apps.analytics.models import RiskFactor, StudentFeatureSnapshot, StudentRiskScore


class StudentRiskScoreModelTest(TestCase):
    """Tests para el modelo StudentRiskScore"""

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

    def test_risk_score_creation(self):
        risk = StudentRiskScore.objects.create(
            student=self.student,
            academic_period=self.period,
            risk_score=Decimal("75.50"),
            risk_label="Alto",
            model_version="v1.0",
        )
        self.assertEqual(risk.risk_score, Decimal("75.50"))
        self.assertEqual(risk.risk_label, "Alto")
        self.assertIsNotNone(risk.calculated_at)

    def test_risk_score_str(self):
        risk = StudentRiskScore.objects.create(
            student=self.student,
            academic_period=self.period,
            risk_score=Decimal("45.00"),
            risk_label="Medio",
            model_version="v1.0",
        )
        self.assertIn("Medio", str(risk))
        self.assertIn("45.00", str(risk))

    def test_risk_score_cascade_delete(self):
        risk = StudentRiskScore.objects.create(
            student=self.student,
            academic_period=self.period,
            risk_score=Decimal("30.00"),
            risk_label="Bajo",
            model_version="v1.0",
        )
        self.student.delete()
        self.assertFalse(StudentRiskScore.objects.filter(pk=risk.pk).exists())

    def test_multiple_risk_scores_ordering(self):
        StudentRiskScore.objects.create(
            student=self.student,
            academic_period=self.period,
            risk_score=Decimal("30.00"),
            risk_label="Bajo",
            model_version="v1.0",
        )
        StudentRiskScore.objects.create(
            student=self.student,
            academic_period=self.period,
            risk_score=Decimal("80.00"),
            risk_label="Alto",
            model_version="v1.0",
        )
        scores = StudentRiskScore.objects.filter(student=self.student)
        self.assertEqual(scores.first().risk_score, Decimal("80.00"))


class StudentFeatureSnapshotModelTest(TestCase):
    """Tests para el modelo StudentFeatureSnapshot"""

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

    def test_snapshot_creation(self):
        snapshot = StudentFeatureSnapshot.objects.create(
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
        self.assertEqual(snapshot.attendance_rate, Decimal("85.00"))
        self.assertEqual(snapshot.failing_subjects_count, 2)
        self.assertIsNotNone(snapshot.calculated_at)

    def test_snapshot_str(self):
        snapshot = StudentFeatureSnapshot.objects.create(
            student=self.student,
            academic_period=self.period,
            attendance_rate=Decimal("90.00"),
            consecutive_absences_max=1,
            tardiness_count=2,
            avg_grade_normalized=Decimal("8.00"),
            grade_trend_slope=Decimal("0.05"),
            failing_subjects_count=0,
            conduct_score=Decimal("9.00"),
            family_notified_ratio=Decimal("0.10"),
            age_grade_gap=0,
        )
        self.assertIn("Maria", str(snapshot))
        self.assertIn("Periodo 1", str(snapshot))

    def test_snapshot_nullable_fields(self):
        snapshot = StudentFeatureSnapshot.objects.create(
            student=self.student,
            academic_period=self.period,
            attendance_rate=Decimal("70.00"),
            consecutive_absences_max=5,
            tardiness_count=10,
            avg_grade_normalized=Decimal("5.00"),
            grade_trend_slope=Decimal("-0.50"),
            failing_subjects_count=4,
            conduct_score=Decimal("4.00"),
            family_notified_ratio=Decimal("0.80"),
            prev_period_avg_grade=None,
            age_grade_gap=1,
        )
        self.assertIsNone(snapshot.prev_period_avg_grade)

    def test_snapshot_cascade_delete(self):
        snapshot = StudentFeatureSnapshot.objects.create(
            student=self.student,
            academic_period=self.period,
            attendance_rate=Decimal("80.00"),
            consecutive_absences_max=2,
            tardiness_count=3,
            avg_grade_normalized=Decimal("6.50"),
            grade_trend_slope=Decimal("0.00"),
            failing_subjects_count=1,
            conduct_score=Decimal("7.00"),
            family_notified_ratio=Decimal("0.20"),
            age_grade_gap=0,
        )
        self.student.delete()
        self.assertFalse(StudentFeatureSnapshot.objects.filter(pk=snapshot.pk).exists())


class RiskFactorModelTest(TestCase):
    def setUp(self):
        self.factor = RiskFactor.objects.create(
            code="ASIST_BAJA",
            name="Asistencia Baja",
            description="Estudiante con alta tasa de inasistencia",
        )

    def test_creation(self):
        self.assertEqual(self.factor.code, "ASIST_BAJA")
        self.assertEqual(self.factor.name, "Asistencia Baja")
        self.assertEqual(self.factor.description, "Estudiante con alta tasa de inasistencia")

    def test_code_unique(self):
        with self.assertRaises(Exception):
            RiskFactor.objects.create(
                code="ASIST_BAJA", name="Duplicado", description="Test"
            )

    def test_str(self):
        self.assertEqual(str(self.factor), "Asistencia Baja")
