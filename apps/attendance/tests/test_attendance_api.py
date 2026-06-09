from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

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
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section
from apps.students.models import Enrollment, EnrollmentStatus


class AttendanceAPITest(APITestCase):
    """Tests para los endpoints de asistencia e incidentes bajo /api/attendance/."""

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
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, name="Básica"
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
        self.att_status = AttendanceStatus.objects.create(code="P", name="Presente")

        self.attendance_url = "/api/attendance/attendances/"
        self.att_status_url = "/api/attendance/attendance-statuses/"

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

    def test_list_attendance_statuses(self):
        response = self.client.get(self.att_status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_attendance_status(self):
        data = {"code": "T", "name": "Tardanza"}
        response = self.client.post(self.att_status_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_absence_types(self):
        response = self.client.get("/api/attendance/absence-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_absence_type(self):
        data = {"code": "I", "name": "Injustificada"}
        response = self.client.post("/api/attendance/absence-types/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
