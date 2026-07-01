from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from apps.academic.academic_period.infrastructure.models import AcademicPeriod
from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.academic.teacher_subject_section.infrastructure.models import TeacherSubjectSection
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.grading.evaluation import BlockComponent, EvaluationBlock, EvaluativeActivity, EvaluationService
from apps.grading.evaluation.infrastructure.models import EvaluativeActivityChangeHistory
from apps.grading.student_note import GradeChangeHistory, StudentNote
from apps.grading.student_note.domain.services import StudentNoteService
from apps.institutions.models import (
    AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section,
)
from apps.students.models import Enrollment


class GradingConstraintsTests(TestCase):
    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2025, 9, 1), end_date=date(2026, 6, 30),
        )
        self.period = AcademicPeriod.objects.create(
            name="P1", school_year=self.school_year,
            start_date=date(2025, 9, 1), end_date=date(2025, 12, 15),
        )
        self.level = AcademicLevel.objects.create(name="EGB")
        self.sublevel = AcademicSublevel.objects.create(
            code="MEDIA", name="Media", academic_level=self.level,
        )
        self.grade = AcademicGrade.objects.create(name="7mo", academic_sublevel=self.sublevel)
        self.section = Section.objects.create(
            code="SEC-A", school_year=self.school_year, parallel="A",
            capacity=30, academic_grade=self.grade,
        )
        self.teacher = create_test_user(email="t-constraints@test.com", dni="3000000101")
        self.student = create_test_student(document_number="3000000102")
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section, enrollment_status="ACT",
        )
        self.subject = Subject.objects.create(name="Mate", code="MAT-C")
        self.config = SubjectAcademicConfig.objects.create(
            subject=self.subject, academic_grade=self.grade, weekly_hours=5,
        )
        self.offering = SubjectOffering.objects.create(
            section=self.section, subject_academic_config=self.config,
        )
        self.tss = TeacherSubjectSection.objects.create(
            user=self.teacher, subject_offering=self.offering,
        )
        self.block = EvaluationBlock.objects.create(
            academic_period=self.period, subject_offering=self.offering,
            name="A", block_type="FORMATIVA", weight_percentage=Decimal("100.00"),
        )
        self.component = BlockComponent.objects.create(
            evaluation_block=self.block, name="A1", internal_weight=Decimal("100.00"),
        )
        self.activity = EvaluativeActivity.objects.create(
            block_component=self.component, teacher_subject_section=self.tss,
            title="Tarea 1", max_score=Decimal("10.00"), internal_weight=Decimal("100.00"),
            due_date=date(2025, 10, 15),
        )

    @patch("apps.grading.student_note.application.validators.timezone.localdate")
    def test_create_activity_rejects_due_date_outside_period(self, mock_today):
        mock_today.return_value = date(2025, 9, 10)
        with self.assertRaises(ValueError) as ctx:
            EvaluationService.create_evaluative_activity(
                block_component_id=self.component.id,
                teacher_subject_section_id=self.tss.id,
                title="Fuera de rango",
                max_score=Decimal("10.00"),
                due_date=date(2026, 1, 10),
                internal_weight=Decimal("100.00"),
            )
        self.assertIn("due_date", ctx.exception.args[0])

    @patch("apps.grading.student_note.application.validators.timezone.localdate")
    def test_create_activity_accepts_due_date_within_period(self, mock_today):
        mock_today.return_value = date(2025, 9, 10)
        activity = EvaluationService.create_evaluative_activity(
            block_component_id=self.component.id,
            teacher_subject_section_id=self.tss.id,
            title="Dentro de rango",
            max_score=Decimal("10.00"),
            due_date=date(2025, 11, 1),
            internal_weight=Decimal("100.00"),
        )
        self.assertEqual(activity.due_date, date(2025, 11, 1))

    @patch("apps.grading.student_note.application.validators.timezone.localdate")
    def test_can_register_grade_within_due_date(self, mock_today):
        mock_today.return_value = date(2025, 10, 10)
        note = StudentNoteService.create_student_note(
            enrollment_id=self.enrollment.id,
            evaluative_activity_id=self.activity.id,
            numeric_score=Decimal("8.00"),
            user_id=self.teacher.id,
        )
        self.assertEqual(note.numeric_score, Decimal("8.00"))

    @patch("apps.grading.student_note.application.validators.timezone.localdate")
    def test_cannot_change_registered_grade_after_due_date(self, mock_today):
        mock_today.return_value = date(2025, 10, 10)
        note = StudentNoteService.create_student_note(
            enrollment_id=self.enrollment.id,
            evaluative_activity_id=self.activity.id,
            numeric_score=Decimal("8.00"),
            user_id=self.teacher.id,
        )
        mock_today.return_value = date(2025, 10, 20)
        with self.assertRaises(ValueError) as ctx:
            StudentNoteService.update_student_note(
                note.id,
                numeric_score=Decimal("9.00"),
                user_id=self.teacher.id,
            )
        self.assertIn("grading", ctx.exception.args[0])

    @patch("apps.grading.student_note.application.validators.timezone.localdate")
    def test_can_change_grade_after_extending_due_date(self, mock_today):
        mock_today.return_value = date(2025, 10, 10)
        note = StudentNoteService.create_student_note(
            enrollment_id=self.enrollment.id,
            evaluative_activity_id=self.activity.id,
            numeric_score=Decimal("8.00"),
            user_id=self.teacher.id,
        )
        mock_today.return_value = date(2025, 10, 20)
        EvaluationService.update_evaluative_activity(
            self.activity.id,
            user_id=self.teacher.id,
            due_date=date(2025, 10, 25),
            reason="Extensión de plazo",
        )
        updated = StudentNoteService.update_student_note(
            note.id,
            numeric_score=Decimal("9.00"),
            user_id=self.teacher.id,
        )
        self.assertEqual(updated.numeric_score, Decimal("9.00"))
        self.assertEqual(GradeChangeHistory.objects.filter(student_note=note).count(), 1)
        self.assertEqual(EvaluativeActivityChangeHistory.objects.count(), 1)

    @patch("apps.grading.student_note.application.validators.timezone.localdate")
    def test_cannot_grade_outside_academic_period(self, mock_today):
        mock_today.return_value = date(2026, 1, 10)
        with self.assertRaises(ValueError) as ctx:
            StudentNoteService.create_student_note(
                enrollment_id=self.enrollment.id,
                evaluative_activity_id=self.activity.id,
                numeric_score=Decimal("8.00"),
            )
        self.assertIn("grading", ctx.exception.args[0])

    @patch("apps.grading.student_note.application.validators.timezone.localdate")
    def test_locked_period_blocks_grading(self, mock_today):
        mock_today.return_value = date(2025, 10, 10)
        self.period.grades_locked = True
        self.period.save(update_fields=["grades_locked"])
        with self.assertRaises(ValueError) as ctx:
            StudentNoteService.create_student_note(
                enrollment_id=self.enrollment.id,
                evaluative_activity_id=self.activity.id,
                numeric_score=Decimal("8.00"),
            )
        self.assertIn("grading", ctx.exception.args[0])

    @patch("apps.grading.student_note.application.validators.timezone.localdate")
    def test_first_grade_after_due_date_within_period_is_allowed(self, mock_today):
        mock_today.return_value = date(2025, 10, 20)
        note = StudentNoteService.create_student_note(
            enrollment_id=self.enrollment.id,
            evaluative_activity_id=self.activity.id,
            numeric_score=Decimal("7.50"),
        )
        self.assertEqual(note.numeric_score, Decimal("7.50"))
        self.assertEqual(GradeChangeHistory.objects.filter(student_note=note).count(), 0)
