"""
Tests del mecanismo automatico de recálculo de PeriodGradeSummary.

Cubre:
- Signal post_save en StudentNote encola la task Celery.
- Signal post_delete en StudentNote encola la task.
- Context manager skip_period_summary_recalc suprime el enqueue.
- Endpoint POST /api/grading/period-grade-summaries/recalculate/
- Endpoint POST /api/grading/period-grade-summaries/recalculate-period/
- Permiso grading.recalculate_grade_summary.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework.test import APIClient

from apps.academic.models import (
    AcademicPeriod,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    TeacherSubjectSection,
)
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.iam.models import Permission, Role, RolePermission, UserRole
from apps.grading.models import (
    ActivityType,
    BlockComponent,
    EvaluationBlock,
    EvaluativeActivity,
    PeriodGradeSummary,
    StudentNote,
)
from apps.grading.signals import skip_period_summary_recalc
from apps.institutions.models import (
    AcademicGrade,
    AcademicLevel,
    AcademicSublevel,
    SchoolYear,
    Section,
)
from apps.students.models import Enrollment


class GradeSummaryAutoRecalcTest(TestCase):
    """
    Verifica que los signals de StudentNote disparan el recalculo del
    PeriodGradeSummary correspondiente (vía Celery task, eager en tests).
    """

    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            name="P1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        self.role = Role.objects.create(name="Docente")
        self.user = create_test_user(
            email="ana@example.com",
            dni="0102030405",
            names="Ana",
            last_names="Perez",
        )
        academic_level = AcademicLevel.objects.create(name="Primaria")
        academic_sublevel = AcademicSublevel.objects.create(
            academic_level=academic_level, code="BASICA", name="Básica"
        )
        academic_grade = AcademicGrade.objects.create(
            academic_sublevel=academic_sublevel, name="7",
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=academic_grade, parallel="A", capacity=30,
        )
        subject = Subject.objects.create(name="Matematica", code="MAT-7A")
        subj_config = SubjectAcademicConfig.objects.create(
            subject=subject, academic_grade=academic_grade, weekly_hours=5,
        )
        offering = SubjectOffering.objects.create(
            section=self.section, subject_academic_config=subj_config,
        )
        self.teacher_subject_section = TeacherSubjectSection.objects.create(
            user=self.user, subject_offering=offering,
        )
        self.offering = offering
        self.student = create_test_student(
            document_number="0912345678", names="Juan",
            last_names="Lopez", birth_date=date(2010, 1, 1),
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section,
            enrollment_status="ACT",
        )
        self.activity_type = ActivityType.objects.create(
            code="EXAMEN", name="Examen"
        )
        self.block = EvaluationBlock.objects.create(
            academic_period=self.period,
            subject_offering=self.offering,
            name="Bloque 1",
            block_type="FORMATIVA",
            weight_percentage=Decimal("100.00"),
        )
        self.component = BlockComponent.objects.create(
            evaluation_block=self.block,
            name="Componente 1",
            internal_weight=Decimal("100.00"),
        )
        self.activity = EvaluativeActivity.objects.create(
            block_component=self.component,
            teacher_subject_section=self.teacher_subject_section,
            title="Examen",
            activity_type=self.activity_type,
            max_score=Decimal("10"),
            internal_weight=Decimal("100.00"),
            due_date=date(2025, 2, 1),
        )

    def test_post_save_creates_period_grade_summary(self):
        self.assertFalse(
            PeriodGradeSummary.objects.filter(
                enrollment=self.enrollment,
                subject_offering=self.offering,
                academic_period=self.period,
            ).exists()
        )

        with self.captureOnCommitCallbacks(execute=True):
            StudentNote.objects.create(
                enrollment=self.enrollment,
                evaluative_activity=self.activity,
                numeric_score=Decimal("8.00"),
            )

        summary = PeriodGradeSummary.objects.get(
            enrollment=self.enrollment,
            subject_offering=self.offering,
            academic_period=self.period,
        )
        self.assertEqual(summary.final_avg_truncated, Decimal("8.00"))
        self.assertFalse(summary.is_failing)
        self.assertEqual(summary.promotion_status, "approved")

    def test_post_save_updates_period_grade_summary(self):
        with self.captureOnCommitCallbacks(execute=True):
            StudentNote.objects.create(
                enrollment=self.enrollment,
                evaluative_activity=self.activity,
                numeric_score=Decimal("8.00"),
            )
        second_activity = EvaluativeActivity.objects.create(
            block_component=self.component,
            teacher_subject_section=self.teacher_subject_section,
            title="Leccion",
            activity_type=self.activity_type,
            max_score=Decimal("10"),
            internal_weight=Decimal("100.00"),
            due_date=date(2025, 2, 15),
        )
        with self.captureOnCommitCallbacks(execute=True):
            StudentNote.objects.create(
                enrollment=self.enrollment,
                evaluative_activity=second_activity,
                numeric_score=Decimal("4.00"),
            )
        summary = PeriodGradeSummary.objects.get(
            enrollment=self.enrollment,
            subject_offering=self.offering,
            academic_period=self.period,
        )
        self.assertEqual(summary.final_avg_truncated, Decimal("6.00"))
        self.assertTrue(summary.is_failing)
        self.assertEqual(summary.promotion_status, "failed")

    def test_post_delete_triggers_recompute(self):
        """
        Al eliminar una nota, la signal dispara el recalculo.
        Con calculate_period_average_for_subject retornando None cuando no hay notas,
        el servicio no modifica el resumen existente (queda con el ultimo valor).
        """
        with self.captureOnCommitCallbacks(execute=True):
            note = StudentNote.objects.create(
                enrollment=self.enrollment,
                evaluative_activity=self.activity,
                numeric_score=Decimal("3.00"),
            )
        self.assertTrue(
            PeriodGradeSummary.objects.filter(
                enrollment=self.enrollment,
                academic_period=self.period,
            ).exists()
        )
        with patch(
            "apps.grading.signals.recompute_period_grade_summary_task.delay"
        ) as mocked_delay:
            with self.captureOnCommitCallbacks(execute=True):
                note.delete()
            mocked_delay.assert_called_once()

    def test_skip_period_summary_recalc_suppresses_signal(self):
        with patch(
            "apps.grading.signals.recompute_period_grade_summary_task.delay"
        ) as mocked_delay:
            with self.captureOnCommitCallbacks(execute=True):
                with skip_period_summary_recalc():
                    StudentNote.objects.create(
                        enrollment=self.enrollment,
                        evaluative_activity=self.activity,
                        numeric_score=Decimal("8.00"),
                    )
            mocked_delay.assert_not_called()

        self.assertFalse(
            PeriodGradeSummary.objects.filter(
                enrollment=self.enrollment,
                academic_period=self.period,
            ).exists()
        )

    def test_post_save_does_call_task_without_skip(self):
        with patch(
            "apps.grading.signals.recompute_period_grade_summary_task.delay"
        ) as mocked_delay:
            with self.captureOnCommitCallbacks(execute=True):
                StudentNote.objects.create(
                    enrollment=self.enrollment,
                    evaluative_activity=self.activity,
                    numeric_score=Decimal("9.00"),
                )
            mocked_delay.assert_called_once()
            args, _ = mocked_delay.call_args
            self.assertEqual(args[0], self.enrollment.id)
            self.assertEqual(args[1], self.offering.id)
            self.assertEqual(args[2], self.period.id)


class GradeSummaryRecalculateAPITest(TestCase):
    """Tests de los endpoints recalculate / recalculate-period."""

    def setUp(self):
        self.client = APIClient()
        self.school_year = SchoolYear.objects.create(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            name="P1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        self.role = Role.objects.create(name="Docente")
        self.user = create_test_user(
            email="ana@example.com",
            dni="0102030405",
            names="Ana",
            last_names="Perez",
        )
        UserRole.objects.create(user=self.user, role=self.role)
        perm = Permission.objects.create(
            code="grading.recalculate_grade_summary",
            description="Recalcular resumen de calificaciones",
        )
        RolePermission.objects.create(role=self.role, permission=perm)
        self.client.force_authenticate(user=self.user)

        academic_level = AcademicLevel.objects.create(name="Primaria")
        academic_sublevel = AcademicSublevel.objects.create(
            academic_level=academic_level, code="BASICA", name="Básica"
        )
        academic_grade = AcademicGrade.objects.create(
            academic_sublevel=academic_sublevel, name="7",
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=academic_grade, parallel="A", capacity=30,
        )
        subject = Subject.objects.create(name="Matematica", code="MAT-7A")
        subj_config = SubjectAcademicConfig.objects.create(
            subject=subject, academic_grade=academic_grade, weekly_hours=5,
        )
        self.offering = SubjectOffering.objects.create(
            section=self.section, subject_academic_config=subj_config,
        )
        teacher_subject_section = TeacherSubjectSection.objects.create(
            user=self.user, subject_offering=self.offering,
        )
        self.student = create_test_student(
            document_number="0912345678", names="Juan",
            last_names="Lopez", birth_date=date(2010, 1, 1),
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section,
            enrollment_status="ACT",
        )
        activity_type = ActivityType.objects.create(
            code="EXAMEN", name="Examen"
        )
        block = EvaluationBlock.objects.create(
            academic_period=self.period,
            subject_offering=self.offering,
            name="Bloque 1",
            block_type="FORMATIVA",
            weight_percentage=Decimal("100.00"),
        )
        component = BlockComponent.objects.create(
            evaluation_block=block,
            name="Componente 1",
            internal_weight=Decimal("100.00"),
        )
        self.activity = EvaluativeActivity.objects.create(
            block_component=component,
            teacher_subject_section=teacher_subject_section,
            title="Examen",
            activity_type=activity_type,
            max_score=Decimal("10"),
            internal_weight=Decimal("100.00"),
            due_date=date(2025, 2, 1),
        )

    def test_recalculate_endpoint_dispatches_task(self):
        from apps.grading.tasks import recompute_period_grade_summary_task
        with patch.object(
            recompute_period_grade_summary_task, "delay",
            return_value=MagicMock(id="fake-id")
        ) as mocked_delay:
            response = self.client.post(
                "/api/grading/period-grade-summaries/recalculate/",
                data={
                    "enrollment_id": self.enrollment.id,
                    "subject_offering_id": self.offering.id,
                    "academic_period_id": self.period.id,
                },
                format="json",
            )
        self.assertEqual(response.status_code, 202)
        body = response.json()["data"]
        self.assertIn("task_id", body)
        self.assertEqual(body["status"], "PENDING")
        mocked_delay.assert_called_once_with(
            self.enrollment.id, self.offering.id, self.period.id
        )

    def test_recalculate_endpoint_validates_payload(self):
        response = self.client.post(
            "/api/grading/period-grade-summaries/recalculate/",
            data={},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])

    def test_recalculate_period_endpoint(self):
        with self.captureOnCommitCallbacks(execute=True):
            StudentNote.objects.create(
                enrollment=self.enrollment,
                evaluative_activity=self.activity,
                numeric_score=Decimal("7.50"),
            )

        response = self.client.post(
            "/api/grading/period-grade-summaries/recalculate-period/",
            data={"academic_period_id": self.period.id},
            format="json",
        )
        self.assertEqual(response.status_code, 202)
        body = response.json()["data"]
        self.assertGreaterEqual(body["summaries_calculated"], 1)
        self.assertTrue(
            PeriodGradeSummary.objects.filter(
                enrollment=self.enrollment,
                academic_period=self.period,
            ).exists()
        )

    def test_recalculate_period_404_for_unknown_period(self):
        response = self.client.post(
            "/api/grading/period-grade-summaries/recalculate-period/",
            data={"academic_period_id": 99999},
            format="json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["ok"])

    def test_recalculate_requires_permission(self):
        from apps.iam.models import Role as RoleModel

        no_perm_user = create_test_user(
            email="noperm@test.com",
            dni="9999999999",
            names="No",
            last_names="Perm",
        )
        noperm_role = RoleModel.objects.create(name="SinPermiso")
        UserRole.objects.create(user=no_perm_user, role=noperm_role)
        self.client.force_authenticate(user=no_perm_user)

        response = self.client.post(
            "/api/grading/period-grade-summaries/recalculate/",
            data={
                "enrollment_id": self.enrollment.id,
                "subject_offering_id": self.offering.id,
                "academic_period_id": self.period.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()["ok"])
