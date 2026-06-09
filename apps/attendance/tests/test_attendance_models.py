from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.academic.models import (
    AcademicPeriod,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    TeacherSubjectSection,
)
from apps.iam.models import Role
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.attendance.models import AbsenceType, AttendanceStatus
from apps.attendance.models import Attendance
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section
from apps.students.models import Enrollment, EnrollmentStatus


class AttendanceModelTest(TestCase):
    """Tests para el modelo Attendance."""

    def setUp(self):
        school_year = SchoolYear.objects.create(
            name="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.period = AcademicPeriod.objects.create(
            school_year=school_year,
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
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, code="MEDIA", name="Media"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel,
            name="7",
            sequence_order=1,
        )
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
        subj_config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.academic_grade,
            weekly_hours=5,
            pedagogical_order=1,
        )
        offering = SubjectOffering.objects.create(
            school_year=school_year,
            section=self.section,
            subject_academic_config=subj_config,
        )
        self.teacher_subject_section = TeacherSubjectSection.objects.create(
            user=self.user,
            subject_offering=offering,
        )
        self.student = create_test_student(
            document_number="0912345678",
            names="Juan",
            last_names="Lopez",
            birth_date=date(2010, 1, 1),
        )
        status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            section=self.section,
            enrollment_status=status,
        )

    def test_attendance_string(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        attendance = Attendance(
            enrollment=self.enrollment,
            teacher_subject_section=self.teacher_subject_section,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        self.assertIn("Juan", str(attendance))

class AttendanceStatusModelTest(TestCase):
    def setUp(self):
        self.status = AttendanceStatus.objects.create(code="P", name="Presente")

    def test_creation(self):
        self.assertEqual(self.status.code, "P")
        self.assertEqual(self.status.name, "Presente")

    def test_code_unique(self):
        with self.assertRaises(Exception):
            AttendanceStatus.objects.create(code="P", name="Duplicado")

    def test_str(self):
        self.assertEqual(str(self.status), "Presente")


class AbsenceTypeModelTest(TestCase):
    def setUp(self):
        self.absence = AbsenceType.objects.create(code="J", name="Justificada")

    def test_creation(self):
        self.assertEqual(self.absence.code, "J")
        self.assertEqual(self.absence.name, "Justificada")

    def test_code_unique(self):
        with self.assertRaises(Exception):
            AbsenceType.objects.create(code="J", name="Duplicado")

    def test_str(self):
        self.assertEqual(str(self.absence), "Justificada")
