"""
Tests de capa de Repositorios para el módulo institutions.
"""

from django.test import TestCase
from apps.institutions.models import SchoolYear, AcademicLevel, AcademicSublevel, AcademicGrade, Section
from apps.institutions.repositories.section_repository import SectionRepository
from apps.institutions.repositories.institution_repo import SchoolYearRepository


class SchoolYearRepositoryTest(TestCase):
    """Tests para SchoolYearRepository."""

    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date="2024-09-01",
            end_date="2025-07-31",
            is_active=True,
        )

    def test_get_by_id_exists(self):
        result = SchoolYearRepository.get_by_id(self.school_year.id)
        self.assertEqual(result, self.school_year)

    def test_get_by_id_not_exists(self):
        result = SchoolYearRepository.get_by_id(99999)
        self.assertIsNone(result)

    def test_get_all(self):
        result = SchoolYearRepository.get_all()
        self.assertGreaterEqual(result.count(), 1)

    def test_create(self):
        from datetime import date
        sy = SchoolYearRepository.create(
            start_date=date(2025, 9, 1),
            end_date=date(2026, 7, 31),
            is_active=True,
        )
        self.assertEqual(sy.start_date.year, 2025)

    def test_update(self):
        from datetime import date
        updated = SchoolYearRepository.update(
            self.school_year.id,
            end_date=date(2025, 12, 31),
        )
        self.assertEqual(updated.end_date.year, 2025)

    def test_delete_hard_delete(self):
        sid = self.school_year.id
        SchoolYearRepository.delete(sid)
        self.assertFalse(SchoolYear.objects.filter(id=sid).exists())

    def test_exists(self):
        self.assertTrue(SchoolYearRepository.exists(id=self.school_year.id))
        self.assertFalse(SchoolYearRepository.exists(id=99999))


class SectionRepositoryTest(TestCase):
    """Tests para SectionRepository."""

    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date="2024-09-01",
            end_date="2025-07-31",
            is_active=True,
        )
        self.academic_level = AcademicLevel.objects.create(name="EGB", code="EGB")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, code="BASICA", name="Básica"
        )
        self.grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel,
            name="8vo",
            code="8VO",
        )
        self.section_a = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.grade,
            parallel="A",
            capacity=30,
            code="SEC_A",
        )
        self.section_b = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.grade,
            parallel="B",
            capacity=25,
            code="SEC_B",
        )

    def test_get_all(self):
        result = SectionRepository.get_all()
        self.assertEqual(result.count(), 2)

    def test_get_all_active_only(self):
        self.section_b.is_active = False
        self.section_b.save()
        result = SectionRepository.get_all(active_only=True)
        self.assertEqual(result.count(), 1)

    def test_get_by_school_year(self):
        result = SectionRepository.get_by_school_year(self.school_year.id)
        self.assertEqual(result.count(), 2)

    def test_get_by_school_year_empty(self):
        new_sy = SchoolYear.objects.create(
            start_date="2025-09-01",
            end_date="2026-07-31",
            is_active=True,
        )
        result = SectionRepository.get_by_school_year(new_sy.id)
        self.assertEqual(result.count(), 0)

    def test_get_by_grade(self):
        result = SectionRepository.get_by_grade(self.grade.id)
        self.assertEqual(result.count(), 2)

    def test_get_by_grade_empty(self):
        new_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, code="SUPERIOR", name="Superior"
        )
        new_grade = AcademicGrade.objects.create(
            academic_sublevel=new_sublevel,
            name="9no",
            code="9NO",
        )
        result = SectionRepository.get_by_grade(new_grade.id)
        self.assertEqual(result.count(), 0)

    def test_get_by_id_exists(self):
        result = SectionRepository.get_by_id(self.section_a.id)
        self.assertEqual(result, self.section_a)

    def test_get_by_id_not_exists(self):
        result = SectionRepository.get_by_id(99999)
        self.assertIsNone(result)

    def test_create(self):
        section = SectionRepository.create(
            school_year=self.school_year,
            academic_grade=self.grade,
            parallel="C",
            capacity=28,
            code="SEC_C",
        )
        self.assertEqual(section.parallel, "C")

    def test_update(self):
        updated = SectionRepository.update(
            self.section_a.id,
            parallel="Z",
            capacity=35,
        )
        self.assertEqual(updated.parallel, "Z")
        self.assertEqual(updated.capacity, 35)

    def test_delete_soft_delete(self):
        sid = self.section_a.id
        SectionRepository.delete(sid)
        self.assertFalse(Section.objects.filter(id=sid, is_active=True).exists())
