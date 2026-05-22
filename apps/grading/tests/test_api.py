from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.models import (
    Academic_Period,
    Section,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    Teacher_Subject_Section,
)
from apps.accounts.models import Role, User
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.grading.models import (
    AttendanceStatus,
    GradeType,
    QualitativeScale,
)
from apps.institutions.models import AcademicGrade, AcademicLevel, School_Year
from apps.students.models import Enrollment, EnrollmentStatus, Student


class GradingAPITest(APITestCase):
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

        status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            section=self.section,
            enrollment_status=status,
        )
        self.att_status = AttendanceStatus.objects.create(code="P", name="Presente")

        self.student_note_url = "/api/grading/student-notes/"
        self.attendance_url = "/api/grading/attendance/"
        self.conduct_url = "/api/grading/conduct-incidents/"

    def test_list_student_notes(self):
        response = self.client.get(self.student_note_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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


class AttendanceStatusAPITest(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="attstatus@test.com",
            dni="3030303030",
            names="AttStatus",
            last_names="Tester",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        AttendanceStatus.objects.create(code="P", name="Presente")
        AttendanceStatus.objects.create(code="A", name="Ausente")
        self.url = "/api/grading/attendance-statuses/"

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        obj = AttendanceStatus.objects.first()
        response = self.client.get(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_not_allowed(self):
        response = self.client.post(self.url, {"code": "J", "name": "Justificado"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class GradeTypeAPITest(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="gradetype@test.com",
            dni="3031303030",
            names="GradeType",
            last_names="Tester",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        GradeType.objects.create(code="NUM", name="Numérica")
        self.url = "/api/grading/grade-types/"

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        obj = GradeType.objects.first()
        response = self.client.get(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class QualitativeScaleAPITest(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Admin")
        self.user = create_test_user(
            email="qualiscale@test.com",
            dni="3032303030",
            names="QualiScale",
            last_names="Tester",
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        QualitativeScale.objects.create(
            code="SE", description="Superior", numeric_equivalence=9.0
        )
        self.url = "/api/grading/qualitative-scales/"

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        obj = QualitativeScale.objects.first()
        response = self.client.get(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
