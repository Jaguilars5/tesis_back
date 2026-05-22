from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.db import IntegrityError

from apps.academic.models import (
    Academic_Period,
    Section,
)
from apps.core.tests.helpers import create_test_student
from apps.institutions.models import AcademicGrade, AcademicLevel, School_Year
from apps.analytics.models import RiskFactor, StudentRiskFactor, StudentRiskScore
from apps.students.models import Student


class StudentRiskScoreModelTest(TestCase):
    """Tests para el modelo StudentRiskScore."""

    def setUp(self):
        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1), end_date=date(2025, 7, 31),
        )
        self.period = Academic_Period.objects.create(
            school_year=self.school_year, name="Periodo 1",
            start_date=date(2024, 9, 1), end_date=date(2024, 12, 15),
        )
        academic_level = AcademicLevel.objects.create(name="Primaria")
        academic_grade = AcademicGrade.objects.create(
            academic_level=academic_level, name="6to", sequence_order=6,
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=academic_grade, parallel="A", capacity=40,
        )
        self.student = create_test_student(
            document_number="1234567890", names="Juan",
            last_names="Perez", birth_date=date(2012, 5, 15),
        )

    def test_create_student_risk_score(self):
        risk = StudentRiskScore.objects.create(
            student=self.student,
            academic_period=self.period,
            risk_score=Decimal("75.50"),
            risk_label="Alto",
            model_version="v1.0",
        )

        self.assertEqual(risk.risk_score, Decimal("75.50"))
        self.assertEqual(risk.risk_label, "Alto")
        self.assertEqual(risk.model_version, "v1.0")
        self.assertIsNotNone(risk.calculated_at)

    def test_student_risk_score_str(self):
        risk = StudentRiskScore.objects.create(
            student=self.student,
            academic_period=self.period,
            risk_score=Decimal("45.00"),
            risk_label="Medio",
            model_version="v1.0",
        )

        self.assertIn("Medio", str(risk))
        self.assertIn("45.00", str(risk))

    def test_student_risk_score_ordering(self):
        StudentRiskScore.objects.create(
            student=self.student, academic_period=self.period,
            risk_score=Decimal("30.00"), risk_label="Bajo",
            model_version="v1.0",
        )
        StudentRiskScore.objects.create(
            student=self.student, academic_period=self.period,
            risk_score=Decimal("80.00"), risk_label="Alto",
            model_version="v1.0",
        )

        scores = StudentRiskScore.objects.filter(student=self.student)
        self.assertEqual(scores.first().risk_score, Decimal("80.00"))


class StudentRiskFactorModelTest(TestCase):
    """Tests para el modelo StudentRiskFactor."""

    def setUp(self):
        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1), end_date=date(2025, 7, 31),
        )
        self.period = Academic_Period.objects.create(
            school_year=self.school_year, name="Periodo 1",
            start_date=date(2024, 9, 1), end_date=date(2024, 12, 15),
        )
        academic_level = AcademicLevel.objects.create(name="Primaria")
        academic_grade = AcademicGrade.objects.create(
            academic_level=academic_level, name="6to", sequence_order=6,
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=academic_grade, parallel="A", capacity=40,
        )
        self.student = create_test_student(
            document_number="1234567890", names="Juan",
            last_names="Perez", birth_date=date(2012, 5, 15),
        )
        self.risk_score = StudentRiskScore.objects.create(
            student=self.student,
            academic_period=self.period,
            risk_score=Decimal("75.50"),
            risk_label="Alto",
            model_version="v1.0",
        )
        self.risk_factor = RiskFactor.objects.create(
            code="ASIST_BAJA",
            name="Asistencia Baja",
            description="Estudiante con alta tasa de inasistencia",
        )

    def test_create_student_risk_factor(self):
        srf = StudentRiskFactor.objects.create(
            student_risk_score=self.risk_score,
            risk_factor=self.risk_factor,
            contribution_weight=Decimal("40.00"),
        )

        self.assertEqual(srf.contribution_weight, Decimal("40.00"))
        self.assertEqual(srf.student_risk_score, self.risk_score)
        self.assertEqual(srf.risk_factor, self.risk_factor)

    def test_student_risk_factor_unique_constraint(self):
        StudentRiskFactor.objects.create(
            student_risk_score=self.risk_score,
            risk_factor=self.risk_factor,
            contribution_weight=Decimal("40.00"),
        )

        with self.assertRaises(IntegrityError):
            StudentRiskFactor.objects.create(
                student_risk_score=self.risk_score,
                risk_factor=self.risk_factor,
                contribution_weight=Decimal("60.00"),
            )

    def test_multiple_factors_per_score(self):
        factor2 = RiskFactor.objects.create(
            code="NOTAS_BAJAS",
            name="Notas Bajas",
            description="Promedio por debajo del minimo",
        )

        StudentRiskFactor.objects.create(
            student_risk_score=self.risk_score,
            risk_factor=self.risk_factor,
            contribution_weight=Decimal("40.00"),
        )
        StudentRiskFactor.objects.create(
            student_risk_score=self.risk_score,
            risk_factor=factor2,
            contribution_weight=Decimal("60.00"),
        )

        factors = StudentRiskFactor.objects.filter(
            student_risk_score=self.risk_score
        )
        self.assertEqual(factors.count(), 2)

    def test_student_risk_factor_str(self):
        srf = StudentRiskFactor.objects.create(
            student_risk_score=self.risk_score,
            risk_factor=self.risk_factor,
            contribution_weight=Decimal("40.00"),
        )

        self.assertIn("Asistencia Baja", str(srf))
        self.assertIn("40.00", str(srf))

    def test_risk_factor_cascade_delete(self):
        srf = StudentRiskFactor.objects.create(
            student_risk_score=self.risk_score,
            risk_factor=self.risk_factor,
            contribution_weight=Decimal("40.00"),
        )

        self.risk_score.delete()
        self.assertFalse(
            StudentRiskFactor.objects.filter(pk=srf.pk).exists()
        )


class RiskFactorModelTest(TestCase):
    """Tests para el modelo RiskFactor."""

    def setUp(self):
        self.factor = RiskFactor.objects.create(
            code="CONDUCTA",
            name="Problemas de Conducta",
            description="Incidentes disciplinarios recurrentes",
        )

    def test_create_risk_factor(self):
        self.assertEqual(self.factor.code, "CONDUCTA")
        self.assertEqual(self.factor.name, "Problemas de Conducta")

    def test_risk_factor_code_unique(self):
        with self.assertRaises(IntegrityError):
            RiskFactor.objects.create(
                code="CONDUCTA", name="Duplicado",
            )

    def test_risk_factor_str(self):
        self.assertEqual(str(self.factor), "Problemas de Conducta")
