from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.models import (PeriodType,
    AcademicPeriod,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    TeacherSubjectSection,
)
from apps.iam.models import Role, User
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.grading.models import QualitativeScale
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section
from apps.students.models import Enrollment, Student


class GradingAPITest(APITestCase):
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
        academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, code="MEDIA", name="Media"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=academic_sublevel,
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
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)
        subj_config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.academic_grade,
            weekly_hours=5        )
        offering = SubjectOffering.objects.create(
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

        self.enrollment = Enrollment.objects.create(
            student=self.student,
            section=self.section,
            enrollment_status="ACT",
        )

        self.student_note_url = "/api/grading/student-notes/"

    def test_list_student_notes(self):
        response = self.client.get(self.student_note_url)
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
