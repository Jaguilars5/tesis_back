from django.test import TestCase
from datetime import date, timedelta
from ..models import Classroom, DocumentType, RoomType, School_Year


class SchoolYearModelTest(TestCase):
    """Tests para el modelo School_Year"""

    def setUp(self):
        """Crear instancias de prueba"""
        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )

    def test_school_year_creation(self):
        """Probar creación de año escolar"""
        self.assertEqual(self.school_year.name, "2024-2025")
        self.assertTrue(self.school_year.active)

    def test_school_year_date_range(self):
        """Probar que las fechas son válidas"""
        self.assertTrue(self.school_year.start_date < self.school_year.end_date)

    def test_school_year_str(self):
        """Probar representación en string"""
        expected = f"2024-2025 - 2024-09-01 - 2025-07-31"
        self.assertEqual(str(self.school_year), expected)

    def test_multiple_school_years(self):
        """Probar múltiples años escolares"""
        school_year_2 = School_Year.objects.create(
            name="2025-2026",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 7, 31),
        )

        self.assertEqual(School_Year.objects.count(), 2)


class ClassroomModelTest(TestCase):
    """Tests para el modelo Classroom"""

    def setUp(self):
        """Crear instancias de prueba"""
        self.room_type = RoomType.objects.create(
            code="AULA", name="Aula de Clase"
        )
        self.classroom = Classroom.objects.create(
            name="101",
            room_type=self.room_type,
            capacity=40,
        )

    def test_classroom_creation(self):
        """Probar creación de aula"""
        self.assertEqual(self.classroom.name, "101")
        self.assertEqual(self.classroom.room_type.name, "Aula de Clase")
        self.assertEqual(self.classroom.capacity, 40)
        self.assertTrue(self.classroom.active)

    def test_classroom_str(self):
        """Probar representación en string"""
        self.assertIn("101", str(self.classroom))

    def test_classroom_capacity(self):
        """Probar capacidad de aula"""
        classrooms = [
            Classroom(
                name="Pequeña",
                room_type=self.room_type,
                capacity=10,
            ),
            Classroom(
                name="Mediana",
                room_type=self.room_type,
                capacity=30,
            ),
            Classroom(
                name="Grande",
                room_type=self.room_type,
                capacity=100,
            ),
        ]
        Classroom.objects.bulk_create(classrooms)

        small = Classroom.objects.get(name="Pequeña")
        large = Classroom.objects.get(name="Grande")

        self.assertEqual(small.capacity, 10)
        self.assertEqual(large.capacity, 100)
        self.assertLess(small.capacity, large.capacity)
