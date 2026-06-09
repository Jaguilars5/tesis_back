from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.academic.models import (
    AcademicPeriod, Subject, SubjectAcademicConfig, SubjectOffering, TeacherSubjectSection,
)
from apps.attendance.models import Attendance, AttendanceStatus, AbsenceType
from apps.attendance.repositories.attendance_repository import AttendanceRepository
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.grading.models import QualitativeScale
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section
from apps.students.models import Enrollment, EnrollmentStatus


class AttendanceRepositoryTest(TestCase):
    """Tests para los repositorios del módulo attendance."""

    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            name="2025", start_date=date(2025, 1, 1), end_date=date(2025, 12, 31),
        )
        self.period = AcademicPeriod.objects.create(
            school_year=self.school_year, name="P1",
            start_date=date(2025, 1, 1), end_date=date(2025, 3, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, name="Básica"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel, name="7", sequence_order=1,
        )
        self.section = Section.objects.create(
            school_year=self.school_year, academic_grade=self.academic_grade,
            parallel="A", capacity=30,
        )
        self.subject = Subject.objects.create(name="Matemática", code="MAT-7A")
        subj_config = SubjectAcademicConfig.objects.create(
            subject=self.subject, academic_grade=self.academic_grade,
            weekly_hours=5, pedagogical_order=1,
        )
        self.offering = SubjectOffering.objects.create(
            school_year=self.school_year, section=self.section,
            subject_academic_config=subj_config,
        )
        self.user = create_test_user(
            email="teacher@test.com", dni="0102030405",
            names="Ana", last_names="Perez",
        )
        self.tss = TeacherSubjectSection.objects.create(
            user=self.user, subject_offering=self.offering,
        )
        self.student = create_test_student(
            document_number="0912345678", names="Juan", last_names="Lopez",
            birth_date=date(2010, 1, 1),
        )
        self.status_enr, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"},
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section,
            enrollment_status=self.status_enr,
        )
        self.absence_type_none = AbsenceType.objects.get_or_create(
            code="none", defaults={"name": "Ninguno"}
        )[0]
        self.absence_type_unjustified = AbsenceType.objects.get_or_create(
            code="unjustified", defaults={"name": "Injustificado"}
        )[0]
        self.absence_type_justified = AbsenceType.objects.get_or_create(
            code="justified", defaults={"name": "Justificado"}
        )[0]

    def test_attendance_create(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        obj = AttendanceRepository.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        self.assertEqual(obj.attendance_date, date(2025, 2, 1))

    def test_attendance_get_by_id(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        att = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        result = AttendanceRepository.get_by_id(att.pk)
        self.assertEqual(result.attendance_date, date(2025, 2, 1))

    def test_attendance_get_all_ordering(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        att1 = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        att2 = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 2),
            attendance_status=att_status,
        )
        results = AttendanceRepository.get_all(active_only=False)
        self.assertEqual(results.first().pk, att2.pk)

    def test_attendance_update(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        att = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        updated = AttendanceRepository.update(att.pk, observation="Llegó tarde")
        self.assertEqual(updated.observation, "Llegó tarde")

    def test_attendance_delete(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        att = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        pk = att.pk
        AttendanceRepository.delete(pk)
        self.assertFalse(Attendance.objects.filter(pk=pk).exists())

    def test_attendance_exists(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        att = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        self.assertTrue(AttendanceRepository.exists(pk=att.pk))
        self.assertFalse(AttendanceRepository.exists(pk=99999))

    def test_attendance_get_by_unique_key(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        result = AttendanceRepository.get_by_unique_key(
            self.enrollment.pk, self.tss.pk, date(2025, 2, 1),
        )
        self.assertIsNotNone(result)

    def test_attendance_get_by_unique_key_not_found(self):
        result = AttendanceRepository.get_by_unique_key(99999, 99999, date(2025, 1, 1))
        self.assertIsNone(result)

    def test_attendance_get_by_enrollment_and_period(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        att = Attendance.objects.create(
            enrollment=self.enrollment,
            teacher_subject_section=self.tss,
            academic_period=self.period,
            attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        results = AttendanceRepository.get_by_enrollment_and_period(
            self.enrollment.pk, self.period.pk,
        )
        self.assertIn(att, results)

    def test_attendance_get_absences_summary(self):
        p_status = AttendanceStatus.objects.create(code="P", name="Presente")
        a_status = AttendanceStatus.objects.create(code="A", name="Ausente")
        Attendance.objects.create(
            enrollment=self.enrollment, teacher_subject_section=self.tss,
            academic_period=self.period, attendance_date=date(2025, 2, 1),
            attendance_status=p_status, absence_type=self.absence_type_none,
        )
        Attendance.objects.create(
            enrollment=self.enrollment, teacher_subject_section=self.tss,
            academic_period=self.period, attendance_date=date(2025, 2, 2),
            attendance_status=a_status, absence_type=self.absence_type_unjustified,
        )
        Attendance.objects.create(
            enrollment=self.enrollment, teacher_subject_section=self.tss,
            academic_period=self.period, attendance_date=date(2025, 2, 3),
            attendance_status=a_status, absence_type=self.absence_type_justified,
        )
        summary = AttendanceRepository.get_absences_summary(
            self.enrollment.pk, self.period.pk,
        )
        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["justified"], 1)
        self.assertEqual(summary["unjustified"], 1)
        self.assertEqual(summary["late"], 0)

    def test_attendance_list_by_filters(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        Attendance.objects.create(
            enrollment=self.enrollment, teacher_subject_section=self.tss,
            academic_period=self.period, attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        results = AttendanceRepository.list_by_filters(
            student_id=self.student.pk,
        )
        self.assertEqual(results.count(), 1)

    def test_attendance_list_by_filters_with_period(self):
        att_status = AttendanceStatus.objects.create(code="P", name="Presente")
        Attendance.objects.create(
            enrollment=self.enrollment, teacher_subject_section=self.tss,
            academic_period=self.period, attendance_date=date(2025, 2, 1),
            attendance_status=att_status,
        )
        results = AttendanceRepository.list_by_filters(
            academic_period_id=self.period.pk,
        )
        self.assertEqual(results.count(), 1)