from django.test import TestCase
from datetime import date
from apps.accounts.models import Person
from apps.institutions.models import AcademicGrade, AcademicLevel, DocumentType, Institution, School_Year
from apps.academic.models import Timing_Regime, Section
from ..models import Student, Student_Representative
from ..services.students_service import StudentService
from apps.core.tests.helpers import create_test_student


def _create_person(document_number, names, last_names, phone="", email=""):
    doc_type = DocumentType.objects.get_or_create(
        code="CC", defaults={"name": "Cédula de Ciudadanía"}
    )[0]
    return Person.objects.create(
        document_type=doc_type,
        document_number=document_number,
        names=names,
        last_names=last_names,
        phone=phone,
        email=email,
    )


class StudentServiceTest(TestCase):
    """Tests para StudentService"""

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
            institution=self.institution, name="Matutina"
        )
        self.academic_level = AcademicLevel.objects.create(
            institution=self.institution, name="Primaria"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_level=self.academic_level, name="6to", sequence_order=6
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            timing_regime=self.timing_regime,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=40,
        )

    def test_create_student(self):
        """Probar creación de estudiante"""
        student = StudentService.create_student(
            document_number="1234567890",
            names="Juan",
            last_names="Pérez García",
            birth_date=date(2012, 5, 15),
        )

        self.assertIsNotNone(student.id)
        self.assertIsNotNone(student.student_code)

    def test_create_student_duplicate_dni(self):
        """Probar que rechaza DNI duplicado"""
        StudentService.create_student(
            document_number="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
        )

        with self.assertRaises(Exception):
            StudentService.create_student(
                document_number="1234567890",
                names="Pedro",
                last_names="García",
                birth_date=date(2011, 3, 20),
            )

    def test_get_student(self):
        """Probar obtención de estudiante"""
        student = create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
        )

        retrieved = StudentService.get_student(student.id)
        self.assertEqual(retrieved.id, student.id)

    def test_list_students_by_section(self):
        """Probar listado por sección"""
        student1 = create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
        )
        student2 = create_test_student(
            document_number="0987654321",
            names="María",
            last_names="García",
            birth_date=date(2012, 6, 20),
        )

        students = StudentService.list_students_by_section(self.section.id)
        self.assertEqual(students.count(), 0)

    def test_deactivate_student(self):
        """Probar desactivación de estudiante"""
        student = create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
        )

        deactivated = StudentService.deactivate_student(student.id)
        self.assertFalse(deactivated.active)

    def test_search_students(self):
        """Probar búsqueda de estudiantes"""
        create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Pérez García",
            birth_date=date(2012, 5, 15),
        )

        results = StudentService.search_students("Pérez")
        self.assertTrue(any(s.get_full_name() == "Juan Pérez García" for s in results))


class StudentRepresentativeServiceTest(TestCase):
    """Tests para servicios de relación Student-Representative"""

    def setUp(self):
        """Crear datos de prueba"""
        self.student = create_test_student(
            document_number="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
        )
        self.rep_person = _create_person(
            document_number="9876543210",
            names="María",
            last_names="Pérez",
            phone="0987654321",
        )

    def test_assign_representative(self):
        """Probar asignación de representante"""
        rel = StudentService.assign_representative(
            student_id=self.student.id, person_id=self.rep_person.id,
            kinship="Madre", is_primary=True,
        )

        self.assertIsNotNone(rel.id)
        self.assertTrue(rel.is_primary)

    def test_assign_representative_duplicate(self):
        """Probar que rechaza asignación duplicada"""
        StudentService.assign_representative(
            student_id=self.student.id, person_id=self.rep_person.id,
            kinship="Madre",
        )

        with self.assertRaises(Exception):
            StudentService.assign_representative(
                student_id=self.student.id, person_id=self.rep_person.id,
                kinship="Madre",
            )

    def test_set_primary_representative(self):
        """Probar establecimiento de representante principal"""
        rep1 = _create_person(
            document_number="1111111111",
            names="María",
            last_names="Pérez",
            phone="0987654321",
        )
        rep2 = _create_person(
            document_number="2222222222",
            names="Pedro",
            last_names="Pérez",
            phone="0987654322",
        )

        StudentService.assign_representative(
            self.student.id, rep1.id, kinship="Madre", is_primary=True,
        )
        StudentService.assign_representative(
            self.student.id, rep2.id, kinship="Padre", is_primary=False,
        )

        StudentService.set_primary_representative(self.student.id, rep2.id)

        primary = Student_Representative.objects.get(
            student=self.student, is_primary=True
        )
        self.assertEqual(primary.person_id, rep2.id)
