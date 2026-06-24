from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
REPLACED AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section
from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.academic.teacher_subject_section.infrastructure.models import TeacherSubjectSection
from apps.core.tests.helpers import create_test_user


class TeacherSubjectSectionAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="teacher@test.com", dni="5555555555",
            names="Teacher", last_names="Tester", is_superuser=True,
        )
        self.teacher = create_test_user(
            email="docente@test.com", dni="6666666666",
            names="Docente", last_names="Asignado",
        )
        self.client.force_authenticate(user=self.user)
        level = AcademicLevel.objects.create(name="Primaria")
        sublevel = AcademicSublevel.objects.create(academic_level=level, name="Básica")
        grade = AcademicGrade.objects.create(academic_sublevel=sublevel, name="6to")
        school_year = SchoolYear.objects.create(start_date=date(2024, 9, 1), end_date=date(2025, 7, 31))
        section = Section.objects.create(school_year=school_year, academic_grade=grade, parallel="A", capacity=40)
        subject = Subject.objects.create(name="Matemáticas", code="MAT-001")
        config = SubjectAcademicConfig.objects.create(subject=subject, academic_grade=grade, weekly_hours=5)
        self.offering = SubjectOffering.objects.create(section=section, subject_academic_config=config)
        self.url = "/api/academic/teacher-subject-sections/"

    def test_create(self):
        data = {"user": self.teacher.id, "subject_offering": self.offering.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
