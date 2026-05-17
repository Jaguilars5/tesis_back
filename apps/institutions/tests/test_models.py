from django.test import TestCase
from datetime import date, timedelta
from ..models import AcademicRegime, Classroom, DocumentType, Institution, RoomType, School_Year


class InstitutionModelTest(TestCase):
    """Tests para el modelo Institution"""

    def setUp(self):
        """Crear instancia de prueba"""
        self.institution = Institution.objects.create(
            name="Colegio Nacional",
            code="CN-001",
            address="Calle Principal 123",
            city="Quito",
        )

    def test_institution_creation(self):
        """Probar creación de institución"""
        self.assertEqual(self.institution.name, "Colegio Nacional")
        self.assertEqual(self.institution.code, "CN-001")
        self.assertTrue(self.institution.active)

    def test_institution_code_unique(self):
        """Probar que código de institución es único"""
        with self.assertRaises(Exception):
            Institution.objects.create(
                name="Otro Colegio",
                code="CN-001",
                address="Otra dirección",
                city="Guayaquil",
            )

    def test_institution_str(self):
        """Probar representación en string"""
        self.assertEqual(str(self.institution), "Colegio Nacional")

    def test_institution_timestamps(self):
        """Probar que timestamps se generan correctamente"""
        self.assertIsNotNone(self.institution.created_at)
        self.assertIsNotNone(self.institution.updated_at)


class SchoolYearModelTest(TestCase):
    """Tests para el modelo School_Year"""

    def setUp(self):
        """Crear instancias de prueba"""
        self.institution = Institution.objects.create(
            name="Instituto Central", code="IC-001", address="Av. Central", city="Quito"
        )
        self.school_year = School_Year.objects.create(
            institution=self.institution,
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )

    def test_school_year_creation(self):
        """Probar creación de año escolar"""
        self.assertEqual(self.school_year.name, "2024-2025")
        self.assertEqual(self.school_year.institution, self.institution)
        self.assertTrue(self.school_year.active)

    def test_school_year_date_range(self):
        """Probar que las fechas son válidas"""
        self.assertTrue(self.school_year.start_date < self.school_year.end_date)

    def test_school_year_str(self):
        """Probar representación en string"""
        expected = f"{self.institution.name} - 2024-09-01 - 2025-07-31"
        self.assertEqual(str(self.school_year), expected)

    def test_multiple_school_years(self):
        """Probar múltiples años escolares en una institución"""
        school_year_2 = School_Year.objects.create(
            institution=self.institution,
            name="2025-2026",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 7, 31),
        )

        years = School_Year.objects.filter(institution=self.institution)
        self.assertEqual(years.count(), 2)


class ClassroomModelTest(TestCase):
    """Tests para el modelo Classroom"""

    def setUp(self):
        """Crear instancias de prueba"""
        self.institution = Institution.objects.create(
            name="Colegio A", code="CA-001", address="Dirección A", city="Quito"
        )
        self.room_type = RoomType.objects.create(
            code="AULA", name="Aula de Clase"
        )
        self.classroom = Classroom.objects.create(
            institution=self.institution,
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
                institution=self.institution,
                name="Pequeña",
                room_type=self.room_type,
                capacity=10,
            ),
            Classroom(
                institution=self.institution,
                name="Mediana",
                room_type=self.room_type,
                capacity=30,
            ),
            Classroom(
                institution=self.institution,
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
