from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, time

from apps.academic.period_type.infrastructure.models import PeriodType
from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.academic.teacher_subject_section.infrastructure.models import TeacherSubjectSection
from apps.institutions.academic_grade.infrastructure.models import AcademicGrade
from apps.institutions.academic_level.infrastructure.models import AcademicLevel
from apps.institutions.academic_sublevel.infrastructure.models import AcademicSublevel
from apps.institutions.school_year.infrastructure.models import SchoolYear
from apps.institutions.section.infrastructure.models import Section
from apps.core.tests.helpers import create_test_user

from ..infrastructure.models import ClassSchedule


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
        sublevel = AcademicSublevel.objects.create(academic_level=level, name="B\u00e1sica")
        grade = AcademicGrade.objects.create(academic_sublevel=sublevel, name="6to")
        school_year = SchoolYear.objects.create(start_date=date(2024, 9, 1), end_date=date(2025, 7, 31))
        section = Section.objects.create(school_year=school_year, academic_grade=grade, parallel="A", capacity=40)
        subject = Subject.objects.create(name="Matem\u00e1ticas", code="MAT-001")
        config = SubjectAcademicConfig.objects.create(subject=subject, academic_grade=grade, weekly_hours=5)
        offering = SubjectOffering.objects.create(section=section, subject_academic_config=config)
        self.tss = TeacherSubjectSection.objects.create(user=self.teacher, subject_offering=offering)
        self.url = "/api/academic/class-schedules/"

    def test_list_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_create(self):
        data = {
            "teacher_subject_section": self.tss.id,
            "day_of_week": 1,
            "start_time": "07:00:00",
            "end_time": "07:45:00",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["ok"])

    def test_get(self):
        obj = ClassSchedule.objects.create(
            teacher_subject_section=self.tss,
            day_of_week=1,
            start_time=time(7, 0),
            end_time=time(7, 45),
        )
        response = self.client.get(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])

    def test_update(self):
        obj = ClassSchedule.objects.create(
            teacher_subject_section=self.tss,
            day_of_week=1,
            start_time=time(7, 0),
            end_time=time(7, 45),
        )
        data = {
            "teacher_subject_section": self.tss.id,
            "day_of_week": 2,
            "start_time": "08:00:00",
            "end_time": "08:45:00",
        }
        response = self.client.put(f"{self.url}{obj.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertEqual(response.data["data"]["day_of_week"], 2)

    def test_destroy(self):
        obj = ClassSchedule.objects.create(
            teacher_subject_section=self.tss,
            day_of_week=1,
            start_time=time(7, 0),
            end_time=time(7, 45),
        )
        response = self.client.delete(f"{self.url}{obj.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])

    def test_soft_delete(self):
        obj = ClassSchedule.objects.create(
            teacher_subject_section=self.tss,
            day_of_week=1,
            start_time=time(7, 0),
            end_time=time(7, 45),
        )
        response = self.client.post(f"{self.url}{obj.id}/soft-delete/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        self.assertFalse(response.data["data"]["is_active"])

    def test_permission_denied(self):
        user_no_perm = create_test_user(
            email="noperm@test.com", dni="9999999999",
            names="No", last_names="Perm", is_superuser=False,
        )
        self.client.force_authenticate(user=user_no_perm)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_by_section_missing_param(self):
        response = self.client.get(f"{self.url}by-section/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_by_section_empty(self):
        response = self.client.get(f"{self.url}by-section/", {"section_id": 99999})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_by_subject(self):
        ClassSchedule.objects.create(
            teacher_subject_section=self.tss,
            day_of_week=1,
            start_time=time(7, 0),
            end_time=time(7, 45),
        )
        response = self.client.get(f"{self.url}?search=Matem")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_by_day(self):
        ClassSchedule.objects.create(
            teacher_subject_section=self.tss,
            day_of_week=1,
            start_time=time(7, 0),
            end_time=time(7, 45),
        )
        ClassSchedule.objects.create(
            teacher_subject_section=self.tss,
            day_of_week=2,
            start_time=time(8, 0),
            end_time=time(8, 45),
        )
        response = self.client.get(f"{self.url}?day_of_week=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
