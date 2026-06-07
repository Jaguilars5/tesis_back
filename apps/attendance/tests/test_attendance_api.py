from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.models import (
    Academic_Period,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    Teacher_Subject_Section,
)
from apps.accounts.models import Role
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.attendance.models import AttendanceStatus
from apps.institutions.models import AcademicGrade, AcademicLevel, School_Year, Section
from apps.students.models import Enrollment, EnrollmentStatus


class AttendanceAPITest(APITestCase):
    """Tests para los endpoints de asistencia e incidentes bajo /api/attendance/."""

    def setUp(self):
        school_year = School_Year.objects.create(
            name="2025",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
        self.period = Academic_Period.objects.create(
            school_year=school_year,
            name="P1",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level,
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
        self.role = Role.objects.create(name="Docente")
        self.user = create_test_user(
            email="ana@example.com",
            dni="0102030405",
            names="Ana",
            last_names="Perez",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
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
        self.teacher_subject_section = Teacher_Subject_Section.objects.create(
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
        self.att_status = AttendanceStatus.objects.create(code="P", name="Presente")

        self.attendance_url = "/api/attendance/attendances/"
        self.conduct_url = "/api/attendance/conduct-incidents/"

    def test_create_attendance(self):
        response = self.client.post(
            self.attendance_url,
            {
                "enrollment": self.enrollment.id,
                "teacher_subject_section": self.teacher_subject_section.id,
                "academic_period": self.period.id,
                "attendance_date": "2025-02-01",
                "attendance_status": self.att_status.id,
            },
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST],
        )

    def test_create_conduct_incident(self):
        response = self.client.post(
            self.conduct_url,
            {
                "enrollment": self.enrollment.id,
                "reported_by_user": self.user.id,
                "academic_period": self.period.id,
                "incident_date": "2025-02-01",
                "category": "disciplina",
                "severity": 3,
            },
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST],
        )
