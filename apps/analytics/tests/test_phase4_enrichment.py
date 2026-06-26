"""
Fase 4 — Enriquecimiento del análisis (PLAN_IMPLEMENTACION.md §5 F).

Verifica las nuevas dimensiones analíticas/segmentación:
- `city` (ciudad de origen), `special_needs_type` (tipo de NEE) y
  `withdrawal_reason` (motivo de retiro) se exponen en
  `feature_builder.build_persistence_metrics` y se persisten en el snapshot.
- El dashboard puede agrupar riesgo y deserción por ciudad y por tipo de NEE,
  y reportar motivos de retiro.

Nota de diseño: estas dimensiones NO son features numéricas del modelo ML
(ciudad = alta cardinalidad; motivo de retiro = variable de resultado). Por eso
el contrato numérico `FEATURE_COLUMNS` permanece sin cambios (no requiere
reentrenamiento).
"""

from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.academic.academic_period import AcademicPeriod
from apps.analytics.student_risk.infrastructure.repositories import StudentFeatureSnapshotRepository
from apps.analytics.dashboard.domain.services import DashboardService
from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder
from apps.analytics.student_risk.infrastructure.models import StudentRiskScore
from apps.core.tests.helpers import create_test_student
from apps.institutions.models import (
    AcademicGrade,
    AcademicLevel,
    AcademicSublevel,
    SchoolYear,
    Section,
)
from apps.people.models import City
from apps.students.models import Enrollment, SpecialNeedsType, WithdrawalReason


class Phase4EnrichmentTest(TestCase):
    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2026, 1, 1), end_date=date(2026, 12, 31)
        )
        self.period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            name="P1",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
        )
        level = AcademicLevel.objects.create(name="Basica")
        sublevel = AcademicSublevel.objects.create(academic_level=level, name="Básica")
        grade = AcademicGrade.objects.create(academic_sublevel=sublevel, name="8")
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=grade,
            parallel="A",
            capacity=30,
        )
        self.quito = City.objects.create(name="Quito", code="UIO")
        self.guayaquil = City.objects.create(name="Guayaquil", code="GYE")
        self.tdah = SpecialNeedsType.objects.create(code="TDAH", name="TDAH")
        self.dislexia = SpecialNeedsType.objects.create(code="DIS", name="Dislexia")
        self.reason_econ = WithdrawalReason.objects.create(code="ECO", name="Económico")
        self.reason_move = WithdrawalReason.objects.create(code="MUD", name="Mudanza")
        self._counter = 0

    def _make_student(self, city, needs_type, status, risk_label, withdrawal_reason=None):
        self._counter += 1
        student = create_test_student(
            document_number=f"09000000{self._counter:02d}",
            names=f"Est{self._counter}",
            last_names="Test",
            birth_date=date(2012, 1, 1),
        )
        person = student.user.person
        person.city = city
        person.save(update_fields=["city"])
        student.special_needs_type = needs_type
        student.save(update_fields=["special_needs_type"])

        enrollment = Enrollment.objects.create(
            student=student,
            section=self.section,
            enrollment_status=status,
            withdrawal_reason=withdrawal_reason,
        )
        StudentRiskScore.objects.create(
            enrollment=enrollment,
            academic_period=self.period,
            risk_score=Decimal("50.00"),
            risk_label=risk_label,
            model_version="test",
        )
        return student, enrollment

    # ——— build_persistence_metrics ———

    def test_build_persistence_metrics_exposes_dimensions(self):
        student, _ = self._make_student(self.quito, self.tdah, "ACT", "rojo")
        builder = AcademicRiskFeatureBuilder(student.id, self.period.id)
        snapshot = builder.build()
        metrics = builder.build_persistence_metrics(snapshot)

        self.assertEqual(metrics["city_id"], self.quito.id)
        self.assertEqual(metrics["special_needs_type_id"], self.tdah.id)
        self.assertIsNone(metrics["withdrawal_reason_id"])

    def test_create_snapshot_persists_dimensions(self):
        _, enrollment = self._make_student(self.quito, self.tdah, "ACT", "rojo")
        snapshot = StudentFeatureSnapshotRepository.create_snapshot(
            enrollment_id=enrollment.id,
            academic_period_id=self.period.id,
            metrics={
                "attendance_rate": Decimal("90.00"),
                "city_id": self.quito.id,
                "special_needs_type_id": self.tdah.id,
                "withdrawal_reason_id": None,
            },
        )
        self.assertEqual(snapshot.city_id, self.quito.id)
        self.assertEqual(snapshot.special_needs_type_id, self.tdah.id)
        self.assertIsNone(snapshot.withdrawal_reason_id)

    # ——— Segmentación de riesgo ———

    def test_risk_distribution_by_city(self):
        self._make_student(self.quito, None, "ACT", "rojo")
        self._make_student(self.quito, None, "ACT", "verde")
        self._make_student(self.guayaquil, None, "ACT", "amarillo")

        dist = DashboardService.get_risk_distribution_by_city(self.period.id)

        self.assertEqual(dist["Quito"]["rojo"], 1)
        self.assertEqual(dist["Quito"]["verde"], 1)
        self.assertEqual(dist["Quito"]["total"], 2)
        self.assertEqual(dist["Guayaquil"]["amarillo"], 1)
        self.assertEqual(dist["Guayaquil"]["total"], 1)

    def test_risk_distribution_by_special_needs_type(self):
        self._make_student(self.quito, self.tdah, "ACT", "rojo")
        self._make_student(self.quito, self.dislexia, "ACT", "amarillo")
        self._make_student(self.quito, None, "ACT", "verde")

        dist = DashboardService.get_risk_distribution_by_special_needs_type(self.period.id)

        self.assertEqual(dist["TDAH"]["rojo"], 1)
        self.assertEqual(dist["Dislexia"]["amarillo"], 1)
        self.assertEqual(dist["Sin NEE"]["verde"], 1)

    # ——— Deserción ———

    def test_dropout_by_city(self):
        self._make_student(self.quito, None, "ACT", "verde")
        self._make_student(self.quito, None, "ACT", "rojo")
        self._make_student(self.guayaquil, None, "RET", "rojo", self.reason_econ)
        self._make_student(self.guayaquil, None, "RET", "amarillo", self.reason_move)

        rows = DashboardService.get_dropout_by_city(self.school_year.id)
        by_city = {r["city"]: r for r in rows}

        self.assertEqual(by_city["Quito"]["total"], 2)
        self.assertEqual(by_city["Quito"]["withdrawn"], 0)
        self.assertEqual(by_city["Quito"]["dropout_rate"], 0.0)
        self.assertEqual(by_city["Guayaquil"]["total"], 2)
        self.assertEqual(by_city["Guayaquil"]["withdrawn"], 2)
        self.assertEqual(by_city["Guayaquil"]["dropout_rate"], 1.0)
        # Ordenado por retiros desc: Guayaquil primero.
        self.assertEqual(rows[0]["city"], "Guayaquil")

    def test_withdrawal_reasons_report(self):
        self._make_student(self.guayaquil, None, "RET", "rojo", self.reason_econ)
        self._make_student(self.guayaquil, None, "RET", "amarillo", self.reason_move)
        self._make_student(self.quito, None, "ACT", "verde")

        report = DashboardService.get_withdrawal_reasons(self.school_year.id)
        by_reason = {r["reason"]: r["count"] for r in report}

        self.assertEqual(by_reason["Económico"], 1)
        self.assertEqual(by_reason["Mudanza"], 1)
        self.assertNotIn("Sin especificar", by_reason)
