from django.test import TestCase
from datetime import date
from apps.institutions.models import Institution, School_Year
from apps.academic.models import Timing_Regime, Section
from ..models import Student, Representative, Student_Representative


class StudentModelTest(TestCase):
    """Tests para el modelo Student"""

    def setUp(self):
        """Crear datos de prueba"""
        self.institution = Institution.objects.create(
            name="Escuela Test", code="ET-001", address="Calle Test", city="Quito"
        )
        self.school_year = School_Year.objects.create(
            institution=self.institution,
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.timing_regime = Timing_Regime.objects.create(
            school_year=self.school_year, name="Matutina"
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            timing_regime=self.timing_regime,
            level="Primaria",
            grade="6to",
            parallel="A",
            capacity=40,
        )

    def test_student_creation(self):
        """Probar creación de estudiante"""
        student = Student.objects.create(
            dni="1234567890",
            names="Juan",
            last_names="Pérez García",
            birth_date=date(2012, 5, 15),
            section=self.section,
        )

        self.assertIsNotNone(student.id)
        self.assertEqual(student.dni, "1234567890")
        self.assertTrue(student.active)

    def test_student_dni_unique(self):
        """Probar que DNI es único"""
        Student.objects.create(
            dni="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
            section=self.section,
        )

        with self.assertRaises(Exception):
            Student.objects.create(
                dni="1234567890",  # Mismo DNI
                names="Pedro",
                last_names="González",
                birth_date=date(2011, 3, 20),
                section=self.section,
            )

    def test_student_str(self):
        """Probar representación en string"""
        student = Student.objects.create(
            dni="1234567890",
            names="Juan",
            last_names="Pérez García",
            birth_date=date(2012, 5, 15),
            section=self.section,
        )

        self.assertEqual(str(student), "Juan Pérez García")

    def test_student_full_name(self):
        """Probar get_full_name"""
        student = Student.objects.create(
            dni="1234567890",
            names="Juan",
            last_names="Pérez García",
            birth_date=date(2012, 5, 15),
            section=self.section,
        )

        self.assertEqual(student.get_full_name(), "Juan Pérez García")

    def test_student_age(self):
        """Probar cálculo de edad"""
        student = Student.objects.create(
            dni="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2010, 5, 15),  # ~14 años
            section=self.section,
        )

        age = student.get_age()
        self.assertGreaterEqual(age, 13)
        self.assertLessEqual(age, 15)


class RepresentativeModelTest(TestCase):
    """Tests para el modelo Representative"""

    def test_representative_creation(self):
        """Probar creación de representante"""
        rep = Representative.objects.create(
            dni="9876543210",
            names="María",
            last_names="Pérez García",
            phone="0987654321",
        )

        self.assertIsNotNone(rep.id)
        self.assertTrue(rep.active)

    def test_representative_dni_unique(self):
        """Probar que DNI es único"""
        Representative.objects.create(
            dni="9876543210",
            names="María",
            last_names="Pérez",
            phone="0987654321",
        )

        with self.assertRaises(Exception):
            Representative.objects.create(
                dni="9876543210",  # Mismo DNI
                names="Ana",
                last_names="García",
                phone="0987654322",
            )

    def test_representative_full_name(self):
        """Probar get_full_name"""
        rep = Representative.objects.create(
            dni="9876543210",
            names="María",
            last_names="Pérez García",
            phone="0987654321",
        )

        self.assertEqual(rep.get_full_name(), "María Pérez García")

    def test_representative_str(self):
        """Probar representación en string"""
        rep = Representative.objects.create(
            dni="9876543210",
            names="María",
            last_names="Pérez García",
            phone="0987654321",
        )

        self.assertEqual(str(rep), "María Pérez García")


class StudentRepresentativeModelTest(TestCase):
    """Tests para el modelo Student_Representative"""

    def setUp(self):
        """Crear datos de prueba"""
        self.institution = Institution.objects.create(
            name="Escuela Test", code="ET-001", address="Calle Test", city="Quito"
        )
        self.school_year = School_Year.objects.create(
            institution=self.institution,
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.timing_regime = Timing_Regime.objects.create(
            school_year=self.school_year, name="Matutina"
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            timing_regime=self.timing_regime,
            level="Primaria",
            grade="6to",
            parallel="A",
            capacity=40,
        )
        self.student = Student.objects.create(
            dni="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
            section=self.section,
        )
        self.representative = Representative.objects.create(
            dni="9876543210",
            names="María",
            last_names="Pérez",
            phone="0987654321",
        )

    def test_relationship_creation(self):
        """Probar creación de relación"""
        rel = Student_Representative.objects.create(
            student=self.student,
            representative=self.representative,
            kinship="Madre",
            is_primary=True,
            can_pickup=True,
        )

        self.assertIsNotNone(rel.id)
        self.assertTrue(rel.is_primary)
        self.assertTrue(rel.can_pickup)

    def test_relationship_unique_together(self):
        """Probar que no puede haber duplicados"""
        Student_Representative.objects.create(
            student=self.student, representative=self.representative, kinship="Madre"
        )

        with self.assertRaises(Exception):
            Student_Representative.objects.create(
                student=self.student,
                representative=self.representative,
                kinship="Madre",
            )

    def test_multiple_representatives(self):
        """Probar múltiples representantes por estudiante"""
        rep2 = Representative.objects.create(
            dni="1111111111",
            names="Pedro",
            last_names="García",
            phone="0987654322",
        )

        Student_Representative.objects.create(
            student=self.student,
            representative=self.representative,
            kinship="Madre",
            is_primary=True,
        )
        Student_Representative.objects.create(
            student=self.student, representative=rep2, kinship="Padre", is_primary=False
        )

        rels = Student_Representative.objects.filter(student=self.student)
        self.assertEqual(rels.count(), 2)
