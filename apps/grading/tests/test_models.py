from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.academic.models import (
    Academic_Activity,
    Academic_Period,
    Config_Academic,
    Section,
    Subject,
    Teacher_Subject_Section,
)
from apps.accounts.models import Role, User
from apps.grading.models import Attendance, ConductIncident, StudentNote
from apps.institutions.models import Institution, School_Year
from apps.students.models import Student


class GradingModelTest(TestCase):
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
            number=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )
        self.activity = Academic_Activity.objects.create(
            config_academic=self.config,
            name="Examen",
            value_max=20,
            weight=1,
            applies_to="all",
            order=1,
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

    def test_student_note_validation(self):
        note = StudentNote(
            student=self.student,
            academic_activity=self.activity,
            academic_period=self.period,
            teacher_subject_section=self.teacher_subject_section,
            note_value=25,
            normalized_value=12.5,
        )
        with self.assertRaises(ValidationError):
            note.full_clean()

    def test_attendance_string(self):
        attendance = Attendance(
            student=self.student,
            teacher_subject_section=self.teacher_subject_section,
            academic_period=self.period,
            date=date(2025, 2, 1),
            status="P",
        )
        self.assertIn("Juan", str(attendance))

    def test_conduct_incident_string(self):
        incident = ConductIncident(
            student=self.student,
            reported_by=self.user,
            academic_period=self.period,
            incident_date=date(2025, 2, 1),
            category="disciplina",
            severity=3,
        )
        self.assertIn("disciplina", str(incident))
