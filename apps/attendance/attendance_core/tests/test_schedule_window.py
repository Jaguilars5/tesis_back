from datetime import date, datetime, time, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from apps.academic.academic_period.infrastructure.models import AcademicPeriod
from apps.academic.class_schedule.infrastructure.models import ClassSchedule
from apps.academic.subject.infrastructure.models import Subject
from apps.academic.subject_academic_config.infrastructure.models import SubjectAcademicConfig
from apps.academic.subject_offering.infrastructure.models import SubjectOffering
from apps.academic.teacher_subject_section.infrastructure.models import TeacherSubjectSection
from apps.attendance.attendance_core.domain.services import AttendanceService
from apps.attendance.attendance_status.infrastructure.models import AttendanceStatus
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.institutions.models import (
    AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section,
)
from apps.students.models import Enrollment


class AttendanceScheduleWindowTests(TestCase):
    def setUp(self):
        today = date.today()
        self.school_year = SchoolYear.objects.create(
            start_date=today.replace(month=1, day=1),
            end_date=today.replace(month=12, day=31),
        )
        self.period = AcademicPeriod.objects.create(
            name="P1", school_year=self.school_year,
            start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=30),
        )
        self.level = AcademicLevel.objects.create(name="EGB")
        self.sublevel = AcademicSublevel.objects.create(
            code="MEDIA", name="Media", academic_level=self.level,
        )
        self.grade = AcademicGrade.objects.create(name="7mo", academic_sublevel=self.sublevel)
        self.section = Section.objects.create(
            code="SEC-A", school_year=self.school_year, parallel="A",
            capacity=30, academic_grade=self.grade,
        )
        self.teacher = create_test_user(email="t-att@test.com", dni="3000000201")
        self.student = create_test_student(document_number="3000000202")
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section, enrollment_status="ACT",
        )
        self.subject = Subject.objects.create(name="Mate", code="MAT-A")
        self.config = SubjectAcademicConfig.objects.create(
            subject=self.subject, academic_grade=self.grade, weekly_hours=5,
        )
        self.offering = SubjectOffering.objects.create(
            section=self.section, subject_academic_config=self.config,
        )
        self.tss = TeacherSubjectSection.objects.create(
            user=self.teacher, subject_offering=self.offering,
        )
        self.schedule = ClassSchedule.objects.create(
            teacher_subject_section=self.tss,
            day_of_week=date.today().isoweekday(),
            start_time=time(8, 0),
            end_time=time(9, 0),
        )
        self.present, _ = AttendanceStatus.objects.get_or_create(
            code="P", defaults={"name": "Presente", "is_active": True},
        )
        self.absent, _ = AttendanceStatus.objects.get_or_create(
            code="A", defaults={"name": "Ausente", "is_active": True},
        )

    @patch("django.utils.timezone.localtime")
    @patch("django.utils.timezone.localdate")
    def test_can_register_during_class(self, mock_localdate, mock_localtime):
        today = date.today()
        mock_localdate.return_value = today
        mock_localtime.return_value = timezone.make_aware(
            datetime.combine(today, time(8, 30))
        )

        attendance = AttendanceService.create_attendance(
            enrollment_id=self.enrollment.id,
            teacher_subject_section_id=self.tss.id,
            academic_period_id=self.period.id,
            attendance_date=today,
            attendance_status_id=self.present.id,
            class_schedule_id=self.schedule.id,
        )
        self.assertEqual(attendance.attendance_status_id, self.present.id)

    @patch("django.utils.timezone.localtime")
    @patch("django.utils.timezone.localdate")
    def test_cannot_modify_after_class_ends(self, mock_localdate, mock_localtime):
        today = date.today()
        mock_localdate.return_value = today
        mock_localtime.return_value = timezone.make_aware(
            datetime.combine(today, time(8, 30))
        )
        AttendanceService.create_attendance(
            enrollment_id=self.enrollment.id,
            teacher_subject_section_id=self.tss.id,
            academic_period_id=self.period.id,
            attendance_date=today,
            attendance_status_id=self.present.id,
            class_schedule_id=self.schedule.id,
        )

        mock_localtime.return_value = timezone.make_aware(
            datetime.combine(today, time(10, 0))
        )
        with self.assertRaises(ValueError) as ctx:
            AttendanceService.create_attendance(
                enrollment_id=self.enrollment.id,
                teacher_subject_section_id=self.tss.id,
                academic_period_id=self.period.id,
                attendance_date=today,
                attendance_status_id=self.absent.id,
                class_schedule_id=self.schedule.id,
            )
        self.assertIn("schedule_time", ctx.exception.args[0])

    @patch("django.utils.timezone.localtime")
    @patch("django.utils.timezone.localdate")
    def test_cannot_register_before_class_starts(self, mock_localdate, mock_localtime):
        today = date.today()
        mock_localdate.return_value = today
        mock_localtime.return_value = timezone.make_aware(
            datetime.combine(today, time(7, 30))
        )
        with self.assertRaises(ValueError) as ctx:
            AttendanceService.create_attendance(
                enrollment_id=self.enrollment.id,
                teacher_subject_section_id=self.tss.id,
                academic_period_id=self.period.id,
                attendance_date=today,
                attendance_status_id=self.present.id,
                class_schedule_id=self.schedule.id,
            )
        self.assertIn("schedule_time", ctx.exception.args[0])

    @patch("django.utils.timezone.localdate")
    def test_cannot_modify_past_registered_attendance(self, mock_localdate):
        past = date.today() - timedelta(days=1)
        self.schedule.day_of_week = past.isoweekday()
        self.schedule.save(update_fields=["day_of_week"])
        mock_localdate.return_value = date.today()
        AttendanceService.create_attendance(
            enrollment_id=self.enrollment.id,
            teacher_subject_section_id=self.tss.id,
            academic_period_id=self.period.id,
            attendance_date=past,
            attendance_status_id=self.present.id,
            class_schedule_id=self.schedule.id,
        )
        with self.assertRaises(ValueError) as ctx:
            AttendanceService.create_attendance(
                enrollment_id=self.enrollment.id,
                teacher_subject_section_id=self.tss.id,
                academic_period_id=self.period.id,
                attendance_date=past,
                attendance_status_id=self.absent.id,
                class_schedule_id=self.schedule.id,
            )
        self.assertIn("schedule_time", ctx.exception.args[0])
