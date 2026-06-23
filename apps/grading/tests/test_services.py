from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.academic.models import (PeriodType,
    AcademicPeriod,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    TeacherSubjectSection,
)
from apps.iam.models import Role, User
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.grading.models import ActivityType
from apps.grading.models import (
    EvaluativeActivity,
    BlockComponent,
    EvaluationBlock,
)
from apps.attendance.models import AttendanceStatus
from apps.grading.services import GradingService
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section
from apps.students.models import Enrollment, Student


class GradingServiceTest(TestCase):
    def setUp(self):
        school_year = SchoolYear.objects.create(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.period = AcademicPeriod.objects.create(
            school_year=school_year,
            name="P1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, code="BASICA", name="Básica"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel,
            name="7"        )
        self.section = Section.objects.create(
            school_year=school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=30,
        )
        self.subject = Subject.objects.create(
            name="Matemática",
            code="MAT-7A",
        )
        self.role = Role.objects.create(name="Docente")
        self.user = create_test_user(
            email="ana@example.com",
            dni="0102030405",
            names="Ana",
            last_names="Perez",
        )
        subj_config = SubjectAcademicConfig.objects.create(
            subject=self.subject, academic_grade=self.academic_grade,
            weekly_hours=5,
        )
        offering = SubjectOffering.objects.create(
            section=self.section,
            subject_academic_config=subj_config,
        )
        self.teacher_subject_section = TeacherSubjectSection.objects.create(
            user=self.user, subject_offering=offering,
        )
        self.offering = offering
        self.student = create_test_student(
            document_number="0912345678",
            names="Juan",
            last_names="Lopez",
            birth_date=date(2010, 1, 1),
        )

        self.activity_type_examen = ActivityType.objects.create(
            code="EXAMEN", name="Examen"
        )

    def _create_enrollment(self):
        return Enrollment.objects.create(
            student=self.student,
            section=self.section,
            enrollment_status="ACT",
        )

    def _create_class_assignment(self):
        macro = EvaluationBlock.objects.create(
            academic_period=self.period,
            subject_offering=self.offering,
            name="Macro 1",
            block_type="FORMATIVA",
            weight_percentage=Decimal("100.00"),
        )
        criteria = BlockComponent.objects.create(
            evaluation_block=macro,
            name="Criterio 1",
            internal_weight=Decimal("100.00"),
        )
        return EvaluativeActivity.objects.create(
            block_component=criteria,
            teacher_subject_section=self.teacher_subject_section,
            title="Examen",
            activity_type=self.activity_type_examen,
            max_score=Decimal("20"),
            internal_weight=Decimal("100.00"),
            due_date=date(2025, 2, 1),
        )

    def test_create_student_note(self):
        enrollment = self._create_enrollment()
        evaluative_activity = self._create_class_assignment()
        note = GradingService.create_student_note(
            enrollment_id=enrollment.id,
            evaluative_activity_id=evaluative_activity.id,
            numeric_score=Decimal("10"),
        )
        self.assertEqual(note.calculate_normalized_value(), Decimal("5.00"))

    def test_create_attendance(self):
        enrollment = self._create_enrollment()
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        attendance = GradingService.create_attendance(
            enrollment_id=enrollment.id,
            teacher_subject_section_id=self.teacher_subject_section.id,
            academic_period_id=self.period.id,
            attendance_date=date(2025, 2, 1),
            attendance_status_id=att_status.id,
        )
        self.assertEqual(attendance.attendance_status.code, "P")

    def test_create_conduct_incident(self):
        enrollment = self._create_enrollment()
        incident = GradingService.create_conduct_incident(
            enrollment_id=enrollment.id,
            academic_period_id=self.period.id,
            incident_date=date(2025, 2, 1),
            category="disciplina",
            severity="GRAVE",
        )
        self.assertEqual(incident.severity.code, "GRAVE")
