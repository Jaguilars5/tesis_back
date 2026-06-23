"""
Fase 2 — Unificación de fuentes de datos (PLAN_IMPLEMENTACION.md §6.3, §6.4).

Verifica:
- §6.3 Asistencia: `AttendanceRepository.get_absences_summary` (alertas) y
  `feature_builder` (riesgo) consumen la MISMA taxonomía canónica
  `attendance_status.code` (P/J/A/T).
- §6.4 Reprobado: `feature_builder` y `early_alert_service` reportan el MISMO
  número de materias reprobadas para el mismo (estudiante, periodo), tomado de
  la fuente única `PeriodGradeSummary.is_failing`.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase

from apps.academic.models import (
    AcademicPeriod,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    TeacherSubjectSection,
)
from apps.analytics.services.early_alert_service import EarlyAlertService
from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder
from apps.attendance.models import Attendance, AttendanceStatus
from apps.attendance.repositories import AttendanceRepository
from apps.core.tests.helpers import create_test_student, create_test_user
from apps.grading.models import PeriodGradeSummary
from apps.grading.repositories.period_grade_summary_repository import (
    PeriodGradeSummaryRepository,
)
from apps.institutions.models import (
    AcademicGrade,
    AcademicLevel,
    AcademicSublevel,
    SchoolYear,
    Section,
)
from apps.students.models import Enrollment


class Phase2UnificationTest(TestCase):
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
        self.grade = AcademicGrade.objects.create(academic_sublevel=sublevel, name="8")
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.grade,
            parallel="A",
            capacity=30,
        )
        self.teacher = create_test_user(
            email="docente.fase2@example.com",
            dni="0102030405",
            names="Ana",
            last_names="Perez",
        )
        self.student = create_test_student(
            document_number="0912345678",
            names="Juan",
            last_names="Lopez",
            birth_date=date(2012, 1, 1),
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            section=self.section,
            enrollment_status="ACT",
        )
        self.statuses = {
            code: AttendanceStatus.objects.get_or_create(code=code, defaults={"name": code})[0]
            for code in ("P", "A", "J", "T")
        }

    def _make_offering(self, code):
        subject = Subject.objects.create(name=f"Materia {code}", code=code)
        config = SubjectAcademicConfig.objects.create(
            subject=subject, academic_grade=self.grade, weekly_hours=5
        )
        return SubjectOffering.objects.create(
            section=self.section, subject_academic_config=config
        )

    def _make_tss(self, offering):
        return TeacherSubjectSection.objects.create(
            user=self.teacher, subject_offering=offering
        )

    def _make_summary(self, offering, is_failing):
        return PeriodGradeSummary.objects.create(
            enrollment=self.enrollment,
            subject_offering=offering,
            academic_period=self.period,
            formative_avg=Decimal("6.00"),
            summative_avg=Decimal("6.00"),
            final_avg_truncated=Decimal("6.00") if is_failing else Decimal("8.00"),
            is_failing=is_failing,
        )

    # ——— §6.3 Asistencia ———

    def test_attendance_taxonomy_is_unified_on_attendance_status(self):
        offering = self._make_offering("MAT")
        tss = self._make_tss(offering)
        sequence = ["P", "P", "A", "J", "T", "A"]
        for index, code in enumerate(sequence):
            Attendance.objects.create(
                enrollment=self.enrollment,
                teacher_subject_section=tss,
                academic_period=self.period,
                attendance_date=date(2026, 1, 10) + timedelta(days=index),
                attendance_status=self.statuses[code],
            )

        summary = AttendanceRepository.get_absences_summary(
            self.enrollment.id, self.period.id
        )
        snapshot = AcademicRiskFeatureBuilder(self.student.id, self.period.id).build()
        asistencia = snapshot["variables"]["asistencia"]

        # La taxonomía canónica (attendance_status) da los mismos conteos en ambos
        # consumidores (alertas vía summary, riesgo vía feature_builder).
        self.assertEqual(summary["total"], 6)
        self.assertEqual(summary["present"], 2)
        self.assertEqual(summary["justified"], asistencia["faltas_justificadas"])
        self.assertEqual(summary["unjustified"], asistencia["faltas_injustificadas"])
        self.assertEqual(summary["late"], asistencia["tardanzas"])
        self.assertEqual(summary["justified"], 1)
        self.assertEqual(summary["unjustified"], 2)
        self.assertEqual(summary["late"], 1)

    def test_absence_type_no_longer_drives_summary(self):
        # Aunque exista absence_type, el conteo se basa SOLO en attendance_status.
        from apps.attendance.models import AbsenceType

        unjustified_type = AbsenceType.objects.create(code="unjustified", name="Injustificada")
        offering = self._make_offering("LEN")
        tss = self._make_tss(offering)
        # Estado J (justificado) pero con absence_type 'unjustified' (inconsistente):
        # la fuente canónica debe contarlo como justified, ignorando absence_type.
        Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=tss,
            academic_period=self.period,
            attendance_date=date(2026, 1, 10),
            attendance_status=self.statuses["J"],
            absence_type=unjustified_type,
        )
        summary = AttendanceRepository.get_absences_summary(
            self.enrollment.id, self.period.id
        )
        self.assertEqual(summary["justified"], 1)
        self.assertEqual(summary["unjustified"], 0)

    # ——— §6.4 Reprobado ———

    def test_feature_builder_and_alerts_report_same_failing_count(self):
        self._make_summary(self._make_offering("MAT"), is_failing=True)
        self._make_summary(self._make_offering("LEN"), is_failing=True)
        self._make_summary(self._make_offering("CCN"), is_failing=False)

        repo_count = PeriodGradeSummaryRepository.count_failing(
            self.enrollment.id, self.period.id
        )
        snapshot = AcademicRiskFeatureBuilder(self.student.id, self.period.id).build()
        builder_count = snapshot["variables"]["calificaciones"]["materias_reprobadas"]

        self.assertEqual(repo_count, 2)
        self.assertEqual(builder_count, 2)
        self.assertEqual(builder_count, repo_count)

    def test_early_alert_uses_same_failing_source(self):
        self._make_summary(self._make_offering("MAT"), is_failing=True)
        self._make_summary(self._make_offering("LEN"), is_failing=True)

        alerts = EarlyAlertService.evaluate_student(self.enrollment, self.period)
        failing_alerts = [a for a in alerts if a.alert_type == "failing_grades"]

        self.assertEqual(len(failing_alerts), 1)
        self.assertIn("2 materias reprobadas", failing_alerts[0].description)

    def test_failing_count_is_period_scoped(self):
        other_period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            name="P2",
            start_date=date(2026, 4, 1),
            end_date=date(2026, 6, 30),
        )
        offering = self._make_offering("MAT")
        # Reprobada en OTRO periodo: no debe contar para el periodo actual.
        PeriodGradeSummary.objects.create(
            enrollment=self.enrollment,
            subject_offering=offering,
            academic_period=other_period,
            formative_avg=Decimal("5.00"),
            summative_avg=Decimal("5.00"),
            final_avg_truncated=Decimal("5.00"),
            is_failing=True,
        )
        self.assertEqual(
            PeriodGradeSummaryRepository.count_failing(self.enrollment.id, self.period.id),
            0,
        )
