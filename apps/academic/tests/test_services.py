from django.test import TestCase
from datetime import date
from decimal import Decimal
from apps.institutions.models import (
    AcademicGrade,
    AcademicLevel,
    AcademicSublevel,
    SchoolYear,
)
from apps.institutions.models import Section
from ..models import PeriodType, Subject
from ..services.academic_service import AcademicService


class AcademicServiceTest(TestCase):
    """Tests para AcademicService"""

    def setUp(self):
        """Crear datos de prueba"""
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

    def test_create_section(self):
        """Probar creación de sección"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            academic_grade_id=self.academic_grade.id,
            parallel="A",
            capacity=40,
        )
        self.assertIsNotNone(section.id)
        self.assertEqual(section.parallel, "A")

    def test_get_section(self):
        """Probar obtención de sección"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            academic_grade_id=self.academic_grade.id,
            parallel="B",
            capacity=35,
        )
        retrieved = AcademicService.get_section(section.id)
        self.assertEqual(retrieved.id, section.id)

    def test_create_subject(self):
        """Probar creación de asignatura"""
        subject = AcademicService.create_subject(
            name="Matemática",
            code="MAT-001",
        )
        self.assertIsNotNone(subject.id)
        self.assertEqual(subject.code, "MAT-001")

    def test_update_section(self):
        """Probar actualización de sección"""
        section = AcademicService.create_section(
            school_year_id=self.school_year.id,
            academic_grade_id=self.academic_grade.id,
            parallel="A",
            capacity=40,
        )
        updated = AcademicService.update_section(section.id, capacity=35)
        self.assertEqual(updated.capacity, 35)

    def test_get_subject(self):
        """Probar obtención de asignatura"""
        subject = AcademicService.create_subject(name="Matemática", code="MAT-002")
        retrieved = AcademicService.get_subject(subject.id)
        self.assertEqual(retrieved.id, subject.id)

    def test_update_subject(self):
        """Probar actualización de asignatura"""
        subject = AcademicService.create_subject(name="Matemática", code="MAT-003")
        updated = AcademicService.update_subject(
            subject.id, name="Matemáticas Avanzadas"
        )
        self.assertEqual(updated.name, "Matemáticas Avanzadas")


class AcademicPeriodServiceTest(TestCase):
    """Tests para validaciónes de negocio de AcademicPeriod."""

    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.trimestre = PeriodType.objects.create(
            code="TRIMESTRE-T", name="Trimestre Test", divisions_per_year=3
        )
        self.bimestre = PeriodType.objects.create(
            code="BIMESTRE-T", name="Bimestre Test", divisions_per_year=4
        )
        self.semestre = PeriodType.objects.create(
            code="SEMESTRE-T", name="Semestre Test", divisions_per_year=2
        )

    def _make_period(self, **overrides):
        defaults = dict(
            name="Periodo X",
            school_year_id=self.school_year.id,
            period_type=self.trimestre,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        defaults.update(overrides)
        return AcademicService.create_academic_period(**defaults)

    def _assert_validation_error(self, ctx, expected_field, expected_msg_substring):
        """Helper: el ValueError.args[0] debe ser un dict {field: msg}."""
        exc = ctx.exception
        self.assertTrue(
            exc.args and isinstance(exc.args[0], dict),
            f"Se esperaba dict en args[0], se obtuvo: {exc.args}",
        )
        errors = exc.args[0]
        self.assertIn(
            expected_field,
            errors,
            f"Se esperaba field={expected_field} en {list(errors.keys())}",
        )
        self.assertIn(expected_msg_substring, errors[expected_field])
        return errors

    def test_create_period_ok(self):
        period = self._make_period(name="Q1")
        self.assertIsNotNone(period.id)
        self.assertEqual(period.name, "Q1")

    def test_cannot_exceed_divisions_per_year_field_period_type(self):
        self._make_period(
            name="Q1", start_date=date(2025, 1, 1), end_date=date(2025, 3, 31)
        )
        self._make_period(
            name="Q2", start_date=date(2025, 4, 1), end_date=date(2025, 6, 30)
        )
        self._make_period(
            name="Q3", start_date=date(2025, 7, 1), end_date=date(2025, 9, 30)
        )
        with self.assertRaises(ValueError) as ctx:
            self._make_period(
                name="Q4-ilegal",
                start_date=date(2025, 10, 1),
                end_date=date(2025, 11, 30),
            )
        self._assert_validation_error(
            ctx, "period_type", "No se pueden crear mas periodos"
        )

    def test_cannot_mix_period_types_field_period_type(self):
        self._make_period(name="Q1")
        with self.assertRaises(ValueError) as ctx:
            self._make_period(
                name="S1",
                period_type=self.semestre,
                start_date=date(2025, 7, 1),
                end_date=date(2025, 8, 31),
            )
        self._assert_validation_error(ctx, "period_type", "Estandar educativo Ecuador")
        errors = ctx.exception.args[0]
        self.assertIn("Trimestre Test", errors["period_type"])

    def test_same_period_type_allowed_across_different_years(self):
        self._make_period(name="Q1-2025")
        other_year = SchoolYear.objects.create(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )
        period = AcademicService.create_academic_period(
            name="Q1-2026",
            school_year_id=other_year.id,
            period_type=self.trimestre,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
        )
        self.assertIsNotNone(period.id)

    def test_dates_outside_school_year_field_school_year(self):
        with self.assertRaises(ValueError) as ctx:
            self._make_period(
                start_date=date(2024, 9, 1),
                end_date=date(2024, 12, 31),
            )
        self._assert_validation_error(ctx, "school_year", "dentro del rango del anio")

    def test_overlapping_periods_field_start_date(self):
        self._make_period(
            name="Q1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 4, 30),
        )
        with self.assertRaises(ValueError) as ctx:
            self._make_period(
                name="Q1-bis",
                start_date=date(2025, 3, 1),
                end_date=date(2025, 5, 31),
            )
        self._assert_validation_error(ctx, "start_date", "superpone")

    def test_non_overlapping_adjacent_periods_allowed(self):
        self._make_period(
            name="Q1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        period = self._make_period(
            name="Q2",
            start_date=date(2025, 4, 1),
            end_date=date(2025, 6, 30),
        )
        self.assertIsNotNone(period.id)

    def test_year_weight_sum_cannot_exceed_100_field_year_weight(self):
        self._make_period(
            name="Q1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            year_weight=Decimal("40.00"),
        )
        self._make_period(
            name="Q2",
            start_date=date(2025, 4, 1),
            end_date=date(2025, 6, 30),
            year_weight=Decimal("30.00"),
        )
        with self.assertRaises(ValueError) as ctx:
            self._make_period(
                name="Q3",
                start_date=date(2025, 7, 1),
                end_date=date(2025, 9, 30),
                year_weight=Decimal("40.00"),
            )
        self._assert_validation_error(ctx, "year_weight", "excede 100%")

    def test_year_weight_at_exactly_100_allowed(self):
        self._make_period(
            name="Q1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            year_weight=Decimal("50.00"),
        )
        period = self._make_period(
            name="Q2",
            start_date=date(2025, 4, 1),
            end_date=date(2025, 6, 30),
            year_weight=Decimal("50.00"),
        )
        self.assertIsNotNone(period.id)

    def test_non_regular_periods_excluded_from_weight_sum(self):
        self._make_period(
            name="Q1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            year_weight=Decimal("40.00"),
        )
        self._make_period(
            name="Recuperacion",
            start_date=date(2025, 11, 1),
            end_date=date(2025, 12, 15),
            is_regular_period=False,
            year_weight=Decimal("50.00"),
        )
        period = self._make_period(
            name="Q2",
            start_date=date(2025, 4, 1),
            end_date=date(2025, 6, 30),
            year_weight=Decimal("50.00"),
        )
        self.assertIsNotNone(period.id)

    def test_start_date_after_end_date_field_start_date(self):
        with self.assertRaises(ValueError) as ctx:
            self._make_period(
                start_date=date(2025, 6, 1),
                end_date=date(2025, 3, 1),
            )
        self._assert_validation_error(ctx, "start_date", "anterior a la fecha de fin")

    def test_update_period_cannot_leave_school_year_range(self):
        period = self._make_period(name="Q1")
        with self.assertRaises(ValueError) as ctx:
            AcademicService.update_academic_period(
                period.id,
                start_date=date(2024, 9, 1),
                end_date=date(2024, 12, 31),
            )
        self._assert_validation_error(ctx, "school_year", "dentro del rango del anio")

    def test_update_period_validates_overlap(self):
        q1 = self._make_period(
            name="Q1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        self._make_period(
            name="Q2",
            start_date=date(2025, 4, 1),
            end_date=date(2025, 6, 30),
        )
        with self.assertRaises(ValueError) as ctx:
            AcademicService.update_academic_period(
                q1.id,
                end_date=date(2025, 5, 1),
            )
        self._assert_validation_error(ctx, "start_date", "superpone")

    def test_update_period_validates_weight_sum(self):
        q1 = self._make_period(
            name="Q1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            year_weight=Decimal("40.00"),
        )
        self._make_period(
            name="Q2",
            start_date=date(2025, 4, 1),
            end_date=date(2025, 6, 30),
            year_weight=Decimal("30.00"),
        )
        with self.assertRaises(ValueError) as ctx:
            AcademicService.update_academic_period(
                q1.id,
                year_weight=Decimal("80.00"),
            )
        self._assert_validation_error(ctx, "year_weight", "excede 100%")
