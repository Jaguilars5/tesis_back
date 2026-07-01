from datetime import date
from decimal import Decimal
from unittest import mock

from django.test import TestCase

from apps.academic.academic_period.infrastructure.models import AcademicPeriod
from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.academic.teacher_subject_section.infrastructure.models import TeacherSubjectSection
from apps.attendance.attendance_core.domain.services import AttendanceService
from apps.attendance.attendance_status import AttendanceStatus
from apps.behavior.behavior_evaluation import BehaviorEvaluation
from apps.behavior.conduct_incident.domain.services import ConductIncidentService
from apps.behavior.incident_type import IncidentType
from apps.behavior.severity import Severity
from apps.core.models import Notification
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.grading.evaluation import BlockComponent, EvaluationBlock
from apps.grading.evaluation.domain.services import EvaluationService
from apps.grading.student_note.domain.services import StudentNoteService
from apps.institutions.models import (
    AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section,
)
from apps.students.models import Enrollment, Kinship, StudentRepresentative


@mock.patch("apps.core.notifications.service.emit_to_user")
class NotificationTriggerTests(TestCase):
    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2025, 9, 1), end_date=date(2026, 6, 30),
        )
        self.period = AcademicPeriod.objects.create(
            name="Primer Trimestre", school_year=self.school_year,
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
        self.teacher = create_test_user(email="teacher@test.com", dni="1111111111")
        self.student = create_test_student(
            document_number="1234567890", names="Juan", last_names="Perez",
            email="student@test.com",
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section, enrollment_status="ACT",
        )
        # Representante con su propio usuario.
        self.rep_user = create_test_user(email="rep@test.com", dni="2222222222")
        self.kinship = Kinship.objects.create(code="MADRE", name="Madre")
        self.rep = StudentRepresentative.objects.create(
            student=self.student, user=self.rep_user, kinship=self.kinship,
            is_primary=True, receives_notifications=True, is_active=True,
        )

        self.subject = Subject.objects.create(name="Matemáticas", code="MAT")
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
            name="Bloque 1", block_type="FORMATIVA", weight_percentage=Decimal("100.00"),
        )
        self.component = BlockComponent.objects.create(
            evaluation_block=self.block, name="Componente 1",
            internal_weight=Decimal("100.00"),
        )
        self.activity = self._make_activity()

    def _make_activity(self, title="Examen"):
        from apps.grading.evaluation import EvaluativeActivity
        return EvaluativeActivity.objects.create(
            block_component=self.component, teacher_subject_section=self.tss,
            title=title, max_score=Decimal("10.00"),
            internal_weight=Decimal("100.00"), due_date=date(2025, 10, 15),
        )

    def _recipient_user_ids(self, notification_type):
        return set(
            Notification.objects.filter(notification_type=notification_type)
            .values_list("recipient_id", flat=True)
        )

    def test_activity_created_notifies_section_students_and_reps(self, _mock_emit):
        with self.captureOnCommitCallbacks(execute=True):
            EvaluationService.create_evaluative_activity(
                block_component_id=self.component.id,
                teacher_subject_section_id=self.tss.id,
                title="Nueva tarea", max_score=Decimal("10.00"),
                internal_weight=Decimal("100.00"), due_date=date(2025, 10, 20),
            )
        recipients = self._recipient_user_ids("ACTIVITY_CREATED")
        self.assertIn(self.student.user_id, recipients)
        self.assertIn(self.rep_user.id, recipients)

    def test_activity_graded_notifies_student_and_reps_only(self, _mock_emit):
        with self.captureOnCommitCallbacks(execute=True):
            StudentNoteService.create_student_note(
                enrollment_id=self.enrollment.id,
                evaluative_activity_id=self.activity.id,
                numeric_score=Decimal("8.00"),
            )
        recipients = self._recipient_user_ids("ACTIVITY_GRADED")
        self.assertEqual(recipients, {self.student.user_id, self.rep_user.id})

    def test_attendance_created_notifies_student_and_reps(self, _mock_emit):
        present = AttendanceStatus.objects.get_or_create(
            code="P", defaults={"name": "Presente"}
        )[0]
        with self.captureOnCommitCallbacks(execute=True):
            AttendanceService.create_attendance(
                enrollment_id=self.enrollment.id,
                teacher_subject_section_id=self.tss.id,
                academic_period_id=self.period.id,
                attendance_date=date(2025, 10, 10),
                attendance_status_id=present.id,
            )
        recipients = self._recipient_user_ids("ATTENDANCE_CREATED")
        self.assertEqual(recipients, {self.student.user_id, self.rep_user.id})

    def test_incident_created_notifies_and_recalculates_conduct(self, _mock_emit):
        severity = Severity.objects.create(code="LEVE", name="Falta leve")
        inc_type = IncidentType.objects.get_or_create(
            code="disciplina", defaults={"name": "Disciplina"}
        )[0]
        with self.captureOnCommitCallbacks(execute=True):
            ConductIncidentService.create_conduct_incident(
                incident_type_id=inc_type.id,
                severity_id=severity.id,
                academic_period_id=self.period.id,
                enrollment_id=self.enrollment.id,
                incident_date=date(2025, 10, 5),
            )
        recipients = self._recipient_user_ids("INCIDENT_CREATED")
        self.assertEqual(recipients, {self.student.user_id, self.rep_user.id})

        # Part 5: el promedio de conducta se recalcula al crear el incidente.
        self.assertTrue(
            BehaviorEvaluation.objects.filter(
                enrollment_id=self.enrollment.id,
                academic_period_id=self.period.id,
            ).exists()
        )

    def test_inactive_rep_not_notified(self, _mock_emit):
        self.rep.is_active = False
        self.rep.save(update_fields=["is_active"])
        with self.captureOnCommitCallbacks(execute=True):
            StudentNoteService.create_student_note(
                enrollment_id=self.enrollment.id,
                evaluative_activity_id=self.activity.id,
                numeric_score=Decimal("7.00"),
            )
        recipients = self._recipient_user_ids("ACTIVITY_GRADED")
        self.assertEqual(recipients, {self.student.user_id})
