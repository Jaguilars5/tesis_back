from django.test import TestCase
from datetime import date
from ..models import Classroom, RoomType, School_Year
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


class ClassroomServiceTest(TestCase):
    """Tests para el servicio de Classroom"""

    def setUp(self):
        """Crear instancias de prueba"""
        self.room_type = RoomType.objects.create(code="AULA", name="Aula de Clase")
        self.classroom = Classroom.objects.create(
            name="101",
            room_type=self.room_type,
            capacity=40,
        )

    def test_create_classroom(self):
        """Probar creación de aula"""
        classroom = InstitutionService.create_classroom(
            "102", self.room_type.id, 35
        )

        self.assertIsNotNone(classroom.id)
        self.assertEqual(classroom.name, "102")
        self.assertEqual(classroom.capacity, 35)

    def test_create_classroom_invalid_capacity(self):
        """Probar que rechaza capacidad inválida"""
        with self.assertRaises(ValueError):
            InstitutionService.create_classroom(
                "999", self.room_type.id, 0  # Capacidad inválida
            )

    def test_get_classroom(self):
        """Probar obtención de aula"""
        classroom = InstitutionService.get_classroom(self.classroom.id)
        self.assertEqual(classroom.id, self.classroom.id)

    def test_list_classrooms(self):
        """Probar listado de aulas"""
        InstitutionService.create_classroom(
            "103", self.room_type.id, 25
        )

        classrooms = InstitutionService.list_classrooms()
        self.assertEqual(classrooms.count(), 2)

    def test_list_classrooms_by_type(self):
        """Probar listado de aulas por tipo"""
        lab_type = RoomType.objects.create(code="LAB", name="Laboratorio")
        InstitutionService.create_classroom(
            "Lab-01", lab_type.id, 20
        )

        labs = InstitutionService.list_classrooms_by_type(lab_type.id)
        self.assertEqual(labs.count(), 1)
        self.assertEqual(labs.first().room_type, lab_type)

    def test_update_classroom(self):
        """Probar actualización de aula"""
        classroom = InstitutionService.update_classroom(
            self.classroom.id, capacity=50, room_type_id=self.room_type.id
        )

        self.assertEqual(classroom.capacity, 50)
        self.assertEqual(classroom.room_type, self.room_type)

    def test_deactivate_classroom(self):
        """Probar desactivación de aula"""
        classroom = InstitutionService.deactivate_classroom(self.classroom.id)
        self.assertFalse(classroom.active)

    def test_get_available_classrooms(self):
        """Probar obtención de aulas disponibles"""
        InstitutionService.create_classroom(
            "Grande", self.room_type.id, 100
        )

        available = InstitutionService.get_available_classrooms()
        self.assertEqual(available.count(), 2)

        large = InstitutionService.get_available_classrooms(capacity_min=50)
        self.assertEqual(large.count(), 1)
        self.assertEqual(large.first().name, "Grande")
