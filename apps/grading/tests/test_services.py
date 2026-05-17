from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.academic.models import (
    Academic_Period,
    Config_Academic,
    Section,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    Teacher_Subject_Section,
)
from apps.accounts.models import Role, User
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.grading.models import AttendanceStatus, ClassAssignment, EvaluationCriteria, EvaluationMacro, EvaluationSubcriteria, GradeType
from apps.grading.services import GradingService
from apps.institutions.models import AcademicGrade, AcademicLevel, Institution, School_Year
from apps.students.models import Enrollment, EnrollmentStatus, Student


class GradingServiceTest(TestCase):
    def setUp(self):
        institution = Institution.objects.create(
            name="Institucion",
            code="INST-1",
            address="Calle 1",
            city="Quito",
        )
        school_year = School_Year.objects.create(
            institution=institution,
            name="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.config = Config_Academic.objects.create(
            school_year=school_year,
            institution=institution,
            name="Año lectivo",
            academic_period_type="trimestre",
            number_of_periods=3,
        )
        self.period = Academic_Period.objects.create(
            config_academic=self.config,
            name="P1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        self.academic_level = AcademicLevel.objects.create(
            institution=institution,
            name="Primaria",
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level,
            name="7",
            sequence_order=1,
        )
        self.section = Section.objects.create(
            school_year=school_year,
            timing_regime=None,
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
            institution=institution,
        )
        subj_config = SubjectAcademicConfig.objects.create(
            subject=self.subject, academic_grade=self.academic_grade,
            weekly_hours=5, pedagogical_order=1,
        )
        offering = SubjectOffering.objects.create(
            school_year=school_year, section=self.section,
            subject_academic_config=subj_config,
        )
        self.teacher_subject_section = Teacher_Subject_Section.objects.create(
            user=self.user, subject_offering=offering,
        )
        self.student = create_test_student(
            document_number="0912345678",
            names="Juan",
            last_names="Lopez",
            birth_date=date(2010, 1, 1),
        )

    def _create_enrollment(self):
        status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )
        return Enrollment.objects.create(
            student=self.student,
            section=self.section,
            enrollment_status=status,
        )

    def _create_class_assignment(self):
        macro = EvaluationMacro.objects.create(
            academic_period=self.period,
            name="Macro 1",
            weight_percentage=Decimal("100.00"),
        )
        criteria = EvaluationCriteria.objects.create(
            evaluation_macro=macro,
            name="Criterio 1",
            internal_weight=Decimal("100.00"),
        )
        subcriteria = EvaluationSubcriteria.objects.create(
            evaluation_criteria=criteria,
            name="Subcriterio 1",
            internal_weight=Decimal("100.00"),
        )
        return ClassAssignment.objects.create(
            evaluation_subcriteria=subcriteria,
            teacher_subject_section=self.teacher_subject_section,
            title="Examen",
            max_score=Decimal("20"),
            due_date=date(2025, 2, 1),
        )

    def test_create_student_note(self):
        enrollment = self._create_enrollment()
        class_assignment = self._create_class_assignment()
        grade_type = GradeType.objects.create(code="NUM", name="Numérica")
        note = GradingService.create_student_note(
            enrollment_id=enrollment.id,
            class_assignment_id=class_assignment.id,
            numeric_score=Decimal("10"),
            grade_type_id=grade_type.id,
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
            reported_by_user_id=self.user.id,
            academic_period_id=self.period.id,
            incident_date=date(2025, 2, 1),
            category="disciplina",
            severity=3,
        )
        self.assertEqual(incident.severity, 3)
