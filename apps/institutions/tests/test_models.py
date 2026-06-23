from django.test import TestCase
from datetime import date
from ..models import SchoolYear


class SchoolYearModelTest(TestCase):
    """Tests para el modelo SchoolYear"""

    def setUp(self):
        """Crear instancias de prueba"""
        self.school_year = SchoolYear.objects.create(
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )

    def test_school_year_creation(self):
        """Probar creación de año escolar"""
        self.assertEqual(self.school_year.start_date, date(2024, 9, 1))
        self.assertTrue(self.school_year.is_active)

    def test_school_year_date_range(self):
        """Probar que las fechas son válidas"""
        self.assertTrue(self.school_year.start_date < self.school_year.end_date)

    def test_school_year_str(self):
        """Probar representación en string"""
        expected = "2024-09-01 - 2025-07-31"
        self.assertEqual(str(self.school_year), expected)

    def test_multiple_school_years(self):
        """Probar múltiples años escolares"""
        school_year_2 = SchoolYear.objects.create(
            start_date=date(2025, 9, 1),
            end_date=date(2026, 7, 31),
        )

        self.assertEqual(SchoolYear.objects.count(), 2)
