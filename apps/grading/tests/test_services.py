from datetime import date

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
from apps.grading.services import GradingService
from apps.institutions.models import Institution, School_Year
from apps.students.models import Student


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

    def test_create_student_note(self):
        note = GradingService.create_student_note(
            student_id=self.student.id,
            academic_activity_id=self.activity.id,
            academic_period_id=self.period.id,
            teacher_subject_section_id=self.teacher_subject_section.id,
            note_value=10,
        )
        self.assertEqual(note.normalized_value, 5)

    def test_create_attendance(self):
        attendance = GradingService.create_attendance(
            student_id=self.student.id,
            teacher_subject_section_id=self.teacher_subject_section.id,
            academic_period_id=self.period.id,
            date=date(2025, 2, 1),
            status="P",
        )
        self.assertEqual(attendance.status, "P")

    def test_create_conduct_incident(self):
        incident = GradingService.create_conduct_incident(
            student_id=self.student.id,
            reported_by_id=self.user.id,
            academic_period_id=self.period.id,
            incident_date=date(2025, 2, 1),
            category="disciplina",
            severity=3,
        )
        self.assertEqual(incident.severity, 3)
