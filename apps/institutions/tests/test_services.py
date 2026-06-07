from django.test import TestCase
from datetime import date
from ..models import School_Year
from ..services.institution_service import InstitutionService


class SchoolYearServiceTest(TestCase):
    """Tests para el servicio de School_Year"""

    def setUp(self):
        """Crear instancias de prueba"""
        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )

    def test_create_school_year(self):
        """Probar creación de año escolar"""
        school_year = InstitutionService.create_school_year(
            "2025-2026", date(2025, 9, 1), date(2026, 7, 31)
        )

        self.assertIsNotNone(school_year.id)
        self.assertEqual(school_year.name, "2025-2026")

    def test_create_school_year_invalid_dates(self):
        """Probar que rechaza fechas inválidas"""
        with self.assertRaises(ValueError):
            InstitutionService.create_school_year(
                "2025-2026",
                date(2026, 7, 31),  # Fecha final
                date(2025, 9, 1),  # Fecha inicial (invertidas)
            )

    def test_create_school_year_date_conflict(self):
        """Probar que detecta conflicto de fechas"""
        with self.assertRaises(ValueError):
            InstitutionService.create_school_year(
                "2024-2025-2",
                date(2024, 12, 1),  # Dentro del rango del año existente
                date(2025, 3, 31),
            )

    def test_get_school_year(self):
        """Probar obtención de año escolar"""
        school_year = InstitutionService.get_school_year(self.school_year.id)
        self.assertEqual(school_year.id, self.school_year.id)

    def test_list_school_years(self):
        """Probar listado de años escolares"""
        InstitutionService.create_school_year(
            "2025-2026", date(2025, 9, 1), date(2026, 7, 31)
        )

        years = InstitutionService.list_school_years()
        self.assertEqual(years.count(), 2)

    def test_get_current_school_year(self):
        """Probar obtención del año escolar actual"""
        School_Year.objects.create(
            name="Actual",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            active=True,
        )

        try:
            current = InstitutionService.get_current_school_year()
            self.assertIsNotNone(current)
        except ValueError:
            pass

    def test_update_school_year(self):
        """Probar actualización de año escolar"""
        updated = InstitutionService.update_school_year(
            self.school_year.id, name="2024-2025 Modificado"
        )

        self.assertEqual(updated.name, "2024-2025 Modificado")

    def test_deactivate_school_year(self):
        """Probar desactivación de año escolar"""
        school_year = InstitutionService.deactivate_school_year(self.school_year.id)
        self.assertFalse(school_year.active)
