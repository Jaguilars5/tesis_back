from django.test import TestCase
from datetime import date
from apps.accounts.models import Person
from apps.institutions.models import AcademicGrade, AcademicLevel, DocumentType, School_Year
from apps.academic.models import Section
from ..models import EnrollmentStatus, Student, Student_Representative
from apps.core.tests.helpers import create_test_student


def _create_person(document_number, names, last_names, phone=""):
    doc_type = DocumentType.objects.get_or_create(
        code="CC", defaults={"name": "Cédula de Ciudadanía"}
    )[0]
    return Person.objects.create(
        document_type=doc_type,
        document_number=document_number,
        names=names,
        last_names=last_names,
        phone=phone,
    )


class StudentModelTest(TestCase):
    """Tests para el modelo Student"""

    def setUp(self):
        """Crear datos de prueba"""
        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level, name="6to", sequence_order=1
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=40,
        )

    def test_student_creation(self):
        """Probar creación de estudiante"""
        student = create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Pérez García",
            birth_date=date(2012, 5, 15),
        )

        self.assertIsNotNone(student.id)
        self.assertEqual(student.person.document_number, "1234567890")
        self.assertTrue(student.active)

    def test_student_dni_unique(self):
        """Probar que DNI es único"""
        create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
        )

        with self.assertRaises(Exception):
            create_test_student(
                document_number="1234567890",  # Mismo DNI
                names="Pedro",
                last_names="González",
                birth_date=date(2011, 3, 20),
            )

    def test_student_str(self):
        """Probar representación en string"""
        student = create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Pérez García",
            birth_date=date(2012, 5, 15),
        )

        self.assertEqual(str(student), "Juan Pérez García")

    def test_student_full_name(self):
        """Probar get_full_name"""
        student = create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Pérez García",
            birth_date=date(2012, 5, 15),
        )

        self.assertEqual(student.get_full_name(), "Juan Pérez García")

    def test_student_age(self):
        """Probar cálculo de edad"""
        student = create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2010, 5, 15),  # ~14 años
        )

        age = student.get_age()
        self.assertGreaterEqual(age, 13)
        self.assertLessEqual(age, 15)


class StudentRepresentativeModelTest(TestCase):
    """Tests para el modelo Student_Representative"""

    def setUp(self):
        """Crear datos de prueba"""
        self.school_year = School_Year.objects.create(
            name="2024-2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level, name="6to", sequence_order=1
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=40,
        )
        self.student = create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
        )
        self.representative = _create_person(
            document_number="9876543210",
            names="María",
            last_names="Pérez",
            phone="0987654321",
        )

    def test_relationship_creation(self):
        """Probar creación de relación"""
        rel = Student_Representative.objects.create(
            student=self.student,
            person=self.representative,
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
            student=self.student, person=self.representative, kinship="Madre"
        )

        with self.assertRaises(Exception):
            Student_Representative.objects.create(
                student=self.student,
                person=self.representative,
                kinship="Madre",
            )

    def test_multiple_representatives(self):
        """Probar múltiples representantes por estudiante"""
        rep2 = _create_person(
            document_number="1111111111",
            names="Pedro",
            last_names="García",
            phone="0987654322",
        )

        Student_Representative.objects.create(
            student=self.student,
            person=self.representative,
            kinship="Madre",
            is_primary=True,
        )
        Student_Representative.objects.create(
            student=self.student, person=rep2, kinship="Padre", is_primary=False
        )

        rels = Student_Representative.objects.filter(student=self.student)
        self.assertEqual(rels.count(), 2)


class EnrollmentStatusModelTest(TestCase):
    def setUp(self):
        self.status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"}
        )

    def test_creation(self):
        self.assertEqual(self.status.code, "ACT")
        self.assertEqual(self.status.name, "Activa")

    def test_code_unique(self):
        with self.assertRaises(Exception):
            EnrollmentStatus.objects.create(code="ACT", name="Duplicado")

    def test_str(self):
        self.assertEqual(str(self.status), "Activa")
