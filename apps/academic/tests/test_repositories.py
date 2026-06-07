from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.academic.models import (
    Academic_Period, InterdisciplinaryProject, Subject, SubjectAcademicConfig,
    SubjectOffering, SubjectProject, Teacher_Subject_Section,
)
from apps.academic.repositories.academic_repo import (
    AcademicPeriodRepository, SubjectAcademicConfigRepository, SubjectOfferingRepository,
    SubjectRepository, TeacherSubjectSectionRepository,
)
from apps.academic.repositories.interdisciplinary_project_repository import (
    InterdisciplinaryProjectRepository, SubjectProjectRepository,
)
from apps.core.tests.helpers import create_test_user
from apps.institutions.models import AcademicGrade, AcademicLevel, School_Year, Section


class AcademicRepositoryTest(TestCase):
    """Tests para los repositorios del módulo academic."""

    def setUp(self):
        self.school_year = School_Year.objects.create(
            name="2025", start_date=date(2025, 1, 1), end_date=date(2025, 12, 31),
        )
        self.period = Academic_Period.objects.create(
            school_year=self.school_year, name="P1",
            start_date=date(2025, 1, 1), end_date=date(2025, 3, 31),
        )
        self.period2 = Academic_Period.objects.create(
            school_year=self.school_year, name="P2",
            start_date=date(2025, 4, 1), end_date=date(2025, 6, 30),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level, name="7", sequence_order=1,
        )
        self.section = Section.objects.create(
            school_year=self.school_year, academic_grade=self.academic_grade,
            parallel="A", capacity=30,
        )
        self.subject1 = Subject.objects.create(name="Matemática", code="MAT-7A")
        self.subject2 = Subject.objects.create(name="Lengua", code="LEN-7A")
        self.config = SubjectAcademicConfig.objects.create(
            subject=self.subject1, academic_grade=self.academic_grade,
            weekly_hours=5, pedagogical_order=1,
        )
        self.config2 = SubjectAcademicConfig.objects.create(
            subject=self.subject2, academic_grade=self.academic_grade,
            weekly_hours=4, pedagogical_order=2,
        )
        self.offering = SubjectOffering.objects.create(
            school_year=self.school_year, section=self.section,
            subject_academic_config=self.config,
        )
        self.user = create_test_user(
            email="teacher@test.com", dni="0102030405",
            names="Ana", last_names="Perez",
        )

    # --- SubjectRepository ---

    def test_subject_create(self):
        obj = SubjectRepository.create(name="Ciencias", code="CIE-7A")
        self.assertEqual(obj.name, "Ciencias")

    def test_subject_get_by_id(self):
        result = SubjectRepository.get_by_id(self.subject1.pk)
        self.assertEqual(result.name, "Matemática")

    def test_subject_get_all_ordering(self):
        results = SubjectRepository.get_all(active_only=False)
        self.assertEqual(results.first().name, "Lengua")

    def test_subject_update(self):
        updated = SubjectRepository.update(self.subject1.pk, name="Matemáticas")
        self.assertEqual(updated.name, "Matemáticas")

    def test_subject_delete(self):
        new_subj = Subject.objects.create(name="Temporal", code="TMP-1")
        pk = new_subj.pk
        SubjectRepository.delete(pk)
        self.assertFalse(Subject.objects.filter(pk=pk).exists())

    def test_subject_exists(self):
        self.assertTrue(SubjectRepository.exists(pk=self.subject1.pk))
        self.assertFalse(SubjectRepository.exists(pk=99999))

    def test_subject_count(self):
        self.assertEqual(SubjectRepository.count(), 2)

    # --- AcademicPeriodRepository ---

    def test_period_create(self):
        obj = AcademicPeriodRepository.create(
            school_year=self.school_year, name="P3",
            start_date=date(2025, 7, 1), end_date=date(2025, 9, 30),
        )
        self.assertEqual(obj.name, "P3")

    def test_period_get_by_id(self):
        result = AcademicPeriodRepository.get_by_id(self.period.pk)
        self.assertEqual(result.name, "P1")

    def test_period_get_all_ordering(self):
        results = AcademicPeriodRepository.get_all(active_only=False)
        self.assertEqual(results.first().name, "P2")

    def test_period_get_by_school_year(self):
        results = AcademicPeriodRepository.get_by_school_year(self.school_year.pk)
        self.assertEqual(results.count(), 2)

    def test_period_update(self):
        updated = AcademicPeriodRepository.update(self.period.pk, name="Primer Quimestre")
        self.assertEqual(updated.name, "Primer Quimestre")

    def test_period_delete(self):
        p = Academic_Period.objects.create(
            school_year=self.school_year, name="Temp",
            start_date=date(2025, 1, 1), end_date=date(2025, 1, 31),
        )
        pk = p.pk
        AcademicPeriodRepository.delete(pk)
        self.assertFalse(Academic_Period.objects.filter(pk=pk).exists())

    def test_period_exists(self):
        self.assertTrue(AcademicPeriodRepository.exists(pk=self.period.pk))
        self.assertFalse(AcademicPeriodRepository.exists(pk=99999))

    # --- TeacherSubjectSectionRepository ---

    def test_tss_create(self):
        obj = TeacherSubjectSectionRepository.create(
            user=self.user, subject_offering=self.offering,
        )
        self.assertEqual(obj.user, self.user)

    def test_tss_get_by_id(self):
        tss = Teacher_Subject_Section.objects.create(
            user=self.user, subject_offering=self.offering,
        )
        result = TeacherSubjectSectionRepository.get_by_id(tss.pk)
        self.assertEqual(result.user.email, "teacher@test.com")

    def test_tss_get_all_ordering(self):
        tss1 = Teacher_Subject_Section.objects.create(
            user=self.user, subject_offering=self.offering,
        )
        tss2 = Teacher_Subject_Section.objects.create(
            user=self.user, subject_offering=self.offering,
        )
        results = TeacherSubjectSectionRepository.get_all(active_only=False)
        self.assertEqual(results.first().pk, tss2.pk)

    def test_tss_get_by_user(self):
        Teacher_Subject_Section.objects.create(
            user=self.user, subject_offering=self.offering,
        )
        results = TeacherSubjectSectionRepository.get_by_user(self.user.pk)
        self.assertEqual(results.count(), 1)

    def test_tss_get_by_user_with_school_year(self):
        Teacher_Subject_Section.objects.create(
            user=self.user, subject_offering=self.offering,
        )
        results = TeacherSubjectSectionRepository.get_by_user(
            self.user.pk, school_year_id=self.school_year.pk,
        )
        self.assertEqual(results.count(), 1)

    def test_tss_get_by_section(self):
        Teacher_Subject_Section.objects.create(
            user=self.user, subject_offering=self.offering,
        )
        results = TeacherSubjectSectionRepository.get_by_section(self.section.pk)
        self.assertEqual(results.count(), 1)

    def test_tss_delete(self):
        tss = Teacher_Subject_Section.objects.create(
            user=self.user, subject_offering=self.offering,
        )
        pk = tss.pk
        TeacherSubjectSectionRepository.delete(pk)
        self.assertFalse(Teacher_Subject_Section.objects.filter(pk=pk).exists())

    # --- SubjectAcademicConfigRepository ---

    def test_config_create(self):
        obj = SubjectAcademicConfigRepository.create(
            subject=self.subject1, academic_grade=self.academic_grade,
            weekly_hours=3, pedagogical_order=3,
        )
        self.assertEqual(obj.weekly_hours, 3)

    def test_config_get_by_id(self):
        result = SubjectAcademicConfigRepository.get_by_id(self.config.pk)
        self.assertEqual(result.subject.name, "Matemática")

    def test_config_get_by_subject(self):
        results = SubjectAcademicConfigRepository.get_by_subject(self.subject1.pk)
        self.assertEqual(results.count(), 1)

    def test_config_get_by_grade(self):
        results = SubjectAcademicConfigRepository.get_by_grade(self.academic_grade.pk)
        self.assertEqual(results.count(), 2)

    def test_config_delete(self):
        c = SubjectAcademicConfig.objects.create(
            subject=self.subject1, academic_grade=self.academic_grade,
            weekly_hours=1, pedagogical_order=99,
        )
        pk = c.pk
        SubjectAcademicConfigRepository.delete(pk)
        self.assertFalse(SubjectAcademicConfig.objects.filter(pk=pk).exists())

    # --- SubjectOfferingRepository ---

    def test_offering_create(self):
        obj = SubjectOfferingRepository.create(
            school_year=self.school_year, section=self.section,
            subject_academic_config=self.config2,
        )
        self.assertEqual(obj.subject_academic_config.subject.name, "Lengua")

    def test_offering_get_by_id(self):
        result = SubjectOfferingRepository.get_by_id(self.offering.pk)
        self.assertIsNotNone(result)

    def test_offering_get_by_section(self):
        results = SubjectOfferingRepository.get_by_section(self.section.pk)
        self.assertEqual(results.count(), 1)

    def test_offering_get_by_school_year(self):
        results = SubjectOfferingRepository.get_by_school_year(self.school_year.pk)
        self.assertEqual(results.count(), 1)

    def test_offering_delete(self):
        o = SubjectOffering.objects.create(
            school_year=self.school_year, section=self.section,
            subject_academic_config=self.config2,
        )
        pk = o.pk
        SubjectOfferingRepository.delete(pk)
        self.assertFalse(SubjectOffering.objects.filter(pk=pk).exists())

    # --- InterdisciplinaryProjectRepository ---

    def test_project_create(self):
        obj = InterdisciplinaryProjectRepository.create(
            academic_period=self.period, title="Proyecto de Ciencias",
            start_date=date(2025, 2, 1), delivery_date=date(2025, 3, 15),
        )
        self.assertEqual(obj.title, "Proyecto de Ciencias")

    def test_project_get_by_id(self):
        proj = InterdisciplinaryProject.objects.create(
            academic_period=self.period, title="Proyecto Test",
            start_date=date(2025, 2, 1), delivery_date=date(2025, 3, 15),
        )
        result = InterdisciplinaryProjectRepository.get_by_id(proj.pk)
        self.assertEqual(result.title, "Proyecto Test")

    def test_project_get_active_by_period(self):
        InterdisciplinaryProject.objects.create(
            academic_period=self.period, title="Activo",
            start_date=date(2025, 2, 1), delivery_date=date(2025, 3, 15),
            active=True,
        )
        InterdisciplinaryProject.objects.create(
            academic_period=self.period, title="Inactivo",
            start_date=date(2025, 2, 1), delivery_date=date(2025, 3, 15),
            active=False,
        )
        results = InterdisciplinaryProjectRepository.get_active_by_period(self.period.pk)
        self.assertEqual(results.count(), 1)

    def test_project_delete(self):
        proj = InterdisciplinaryProject.objects.create(
            academic_period=self.period, title="Temp",
            start_date=date(2025, 2, 1), delivery_date=date(2025, 3, 15),
        )
        pk = proj.pk
        InterdisciplinaryProjectRepository.delete(pk)
        self.assertFalse(InterdisciplinaryProject.objects.filter(pk=pk).exists())

    # --- SubjectProjectRepository ---

    def test_subject_project_create(self):
        proj = InterdisciplinaryProject.objects.create(
            academic_period=self.period, title="Proyecto",
            start_date=date(2025, 2, 1), delivery_date=date(2025, 3, 15),
        )
        obj = SubjectProjectRepository.create(
            interdisciplinary_project=proj, subject_offering=self.offering,
        )
        self.assertEqual(obj.interdisciplinary_project.title, "Proyecto")

    def test_subject_project_delete(self):
        proj = InterdisciplinaryProject.objects.create(
            academic_period=self.period, title="Proyecto",
            start_date=date(2025, 2, 1), delivery_date=date(2025, 3, 15),
        )
        sp = SubjectProject.objects.create(
            interdisciplinary_project=proj, subject_offering=self.offering,
        )
        pk = sp.pk
        SubjectProjectRepository.delete(pk)
        self.assertFalse(SubjectProject.objects.filter(pk=pk).exists())
