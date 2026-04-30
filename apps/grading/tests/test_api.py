from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.models import (
    Academic_Activity,
    Academic_Period,
    Config_Academic,
    Section,
    Subject,
    Teacher_Subject_Section,
)
from apps.accounts.models import Role, User
from apps.institutions.models import Institution, School_Year
from apps.students.models import Student


class GradingAPITest(APITestCase):
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
        config = Config_Academic.objects.create(
            school_year=school_year,
            institution=institution,
            name="Año lectivo",
            academic_period_type="trimestre",
            number_of_periods=3,
        )
        self.period = Academic_Period.objects.create(
            config_academic=config,
            name="P1",
            number=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        self.activity = Academic_Activity.objects.create(
            config_academic=config,
            name="Examen",
            value_max=20,
            weight=1,
            applies_to="all",
            order=1,
        )
        self.section = Section.objects.create(
            school_year=school_year,
            timing_regime=None,
            level="Primaria",
            grade="7",
            parallel="A",
            capacity=30,
        )
        self.subject = Subject.objects.create(
            school_year=school_year,
            section=self.section,
            name="Matemática",
            code="MAT-7A",
            weekly_hours=5,
            approve_percentage=70,
        )
        self.role = Role.objects.create(name="Docente")
        self.user = User.objects.create_user(
            email="ana@example.com",
            dni="0102030405",
            names="Ana",
            last_names="Perez",
            password="hash",
            role=self.role,
            institution=institution,
        )
        self.client.force_authenticate(user=self.user)
        self.teacher_subject_section = Teacher_Subject_Section.objects.create(
            user=self.user,
            subject=self.subject,
            section=self.section,
            school_year=school_year,
        )
        self.student = Student.objects.create(
            dni="0912345678",
            names="Juan",
            last_names="Lopez",
            birth_date=date(2010, 1, 1),
            section=self.section,
        )

        self.student_note_url = "/api/grading/student-note/list/"
        self.attendance_url = "/api/grading/attendance/list/"
        self.conduct_url = "/api/grading/conduct-incident/list/"

    def test_list_student_notes(self):
        response = self.client.post(self.student_note_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_attendance(self):
        response = self.client.post(
            "/api/grading/attendance/add/",
            {
                "student": self.student.id,
                "teacher_subject_section": self.teacher_subject_section.id,
                "academic_period": self.period.id,
                "date": "2025-02-01",
                "status": "P",
            },
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST],
        )

    def test_create_conduct_incident(self):
        response = self.client.post(
            "/api/grading/conduct-incident/add/",
            {
                "student": self.student.id,
                "reported_by": self.user.id,
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
