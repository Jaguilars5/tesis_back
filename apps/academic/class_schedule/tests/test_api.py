from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, time
REPLACED AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section
from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.academic.teacher_subject_section.infrastructure.models import TeacherSubjectSection
from apps.core.tests.helpers import create_test_user


class ClassScheduleAPITest(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            email="schedule@test.com", dni="7777777777",
            names="Schedule", last_names="Tester", is_superuser=True,
        )
        self.teacher = create_test_user(
            email="profesor@test.com", dni="8888888888",
            names="Profesor", last_names="Uno",
        )
        self.client.force_authenticate(user=self.user)
        level = AcademicLevel.objects.create(name="Primaria")
        sublevel = AcademicSublevel.objects.create(academic_level=level, name="Básica")
        grade = AcademicGrade.objects.create(academic_sublevel=sublevel, name="6to")
        school_year = SchoolYear.objects.create(start_date=date(2024, 9, 1), end_date=date(2025, 7, 31))
        section = Section.objects.create(school_year=school_year, academic_grade=grade, parallel="A", capacity=40)
        subject = Subject.objects.create(name="Matemáticas", code="MAT-001")
        config = SubjectAcademicConfig.objects.create(subject=subject, academic_grade=grade, weekly_hours=5)
        offering = SubjectOffering.objects.create(section=section, subject_academic_config=config)
        self.tss = TeacherSubjectSection.objects.create(user=self.teacher, subject_offering=offering)
        self.url = "/api/academic/class-schedules/"

    def test_create(self):
        data = {
            "teacher_subject_section": self.tss.id,
            "day_of_week": 1,
            "start_time": "07:00:00",
            "end_time": "07:45:00",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_by_section_missing_param(self):
        response = self.client.get(f"{self.url}by-section/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_by_section_empty(self):
        response = self.client.get(f"{self.url}by-section/", {"section_id": 99999})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
