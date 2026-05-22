from datetime import date
from django.test import TestCase
from django.db import IntegrityError
from apps.accounts.models import Person
from apps.institutions.models import (
    AcademicGrade, AcademicLevel, DocumentType, School_Year,
)
from apps.academic.models import Section
from apps.students.models import Enrollment, EnrollmentStatus, Student
from apps.students.services.enrollment_service import EnrollmentService
from apps.core.tests.helpers import create_test_student


class EnrollmentModelTest(TestCase):
    """Tests para el modelo Enrollment."""

    def setUp(self):
        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level, name="6to", sequence_order=1
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=40,
        )
        self.student = create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Perez",
            birth_date=date(2012, 5, 15),
        )
        self.status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )

    def test_create_enrollment(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            section=self.section,
            enrollment_status=self.status,
        )

        self.assertIsNotNone(enrollment.id)
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.section, self.section)
        self.assertEqual(enrollment.enrollment_status.code, "ACT")
        self.assertIsNotNone(enrollment.enrollment_date)

    def test_enrollment_unique_together(self):
        Enrollment.objects.create(
            student=self.student,
            section=self.section,
            enrollment_status=self.status,
        )

        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(
                student=self.student,
                section=self.section,
                enrollment_status=self.status,
            )

    def test_enrollment_str(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            section=self.section,
            enrollment_status=self.status,
        )

        self.assertIn("Juan Perez", str(enrollment))
        self.assertIn("Activa", str(enrollment))


class EnrollmentServiceTest(TestCase):
    """Tests para EnrollmentService."""

    def setUp(self):
        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level, name="6to", sequence_order=1
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=40,
        )
        self.second_section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.academic_grade,
            parallel="B",
            capacity=40,
        )
        self.student = create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Perez",
            birth_date=date(2012, 5, 15),
        )

    def test_enroll_student(self):
        enrollment = EnrollmentService.enroll_student(
            student=self.student,
            section=self.section,
            enrollment_date=date(2024, 9, 1),
        )

        self.assertIsNotNone(enrollment.id)
        self.assertEqual(enrollment.enrollment_status.code, "ACT")

    def test_enroll_student_already_active(self):
        EnrollmentService.enroll_student(
            student=self.student, section=self.section,
        )

        with self.assertRaises(ValueError) as context:
            EnrollmentService.enroll_student(
                student=self.student, section=self.second_section,
            )

        self.assertIn("ya tiene una matr", str(context.exception))

    def test_withdraw_student(self):
        enrollment = EnrollmentService.enroll_student(
            student=self.student, section=self.section,
        )

        withdrawn = EnrollmentService.withdraw_student(
            enrollment, reason="Retiro voluntario"
        )

        self.assertEqual(withdrawn.enrollment_status.code, "RET")

    def test_get_active_enrollment(self):
        enrollment = EnrollmentService.enroll_student(
            student=self.student, section=self.section,
        )

        active = EnrollmentService.get_active_enrollment(self.student)
        self.assertIsNotNone(active)
        self.assertEqual(active.id, enrollment.id)

    def test_get_active_enrollment_after_withdraw(self):
        enrollment = EnrollmentService.enroll_student(
            student=self.student, section=self.section,
        )
        EnrollmentService.withdraw_student(enrollment)

        active = EnrollmentService.get_active_enrollment(self.student)
        self.assertIsNone(active)
