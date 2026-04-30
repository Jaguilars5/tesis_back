from django.test import TestCase
from datetime import date
from apps.institutions.models import Institution, School_Year
from apps.academic.models import Timing_Regime, Section
from ..models import Student, Representative, Student_Representative
from ..services.students_service import StudentService


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

    def test_create_student(self):
        """Probar creación de estudiante"""
        student = StudentService.create_student(
            dni="1234567890",
            names="Juan",
            last_names="Pérez García",
            birth_date=date(2012, 5, 15),
            section_id=self.section.id,
            enrollment_number="MAT-2024-001",
        )

        self.assertIsNotNone(student.id)
        self.assertEqual(student.enrollment_number, "MAT-2024-001")

    def test_create_student_duplicate_dni(self):
        """Probar que rechaza DNI duplicado"""
        StudentService.create_student(
            dni="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
            section_id=self.section.id,
        )

        with self.assertRaises(ValueError):
            StudentService.create_student(
                dni="1234567890",
                names="Pedro",
                last_names="García",
                birth_date=date(2011, 3, 20),
                section_id=self.section.id,
            )

    def test_get_student(self):
        """Probar obtención de estudiante"""
        student = StudentService.create_student(
            dni="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
            section_id=self.section.id,
        )

        retrieved = StudentService.get_student(student.id)
        self.assertEqual(retrieved.id, student.id)

    def test_list_students_by_section(self):
        """Probar listado por sección"""
        StudentService.create_student(
            dni="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
            section_id=self.section.id,
        )
        StudentService.create_student(
            dni="0987654321",
            names="María",
            last_names="García",
            birth_date=date(2012, 6, 20),
            section_id=self.section.id,
        )

        students = StudentService.list_students_by_section(self.section.id)
        self.assertEqual(students.count(), 2)

    def test_update_student(self):
        """Probar actualización de estudiante"""
        student = StudentService.create_student(
            dni="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
            section_id=self.section.id,
        )

        updated = StudentService.update_student(student.id, names="Juan Pablo")
        self.assertEqual(updated.names, "Juan Pablo")

    def test_deactivate_student(self):
        """Probar desactivación de estudiante"""
        student = StudentService.create_student(
            dni="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
            section_id=self.section.id,
        )

        deactivated = StudentService.deactivate_student(student.id)
        self.assertFalse(deactivated.active)

    def test_search_students(self):
        """Probar búsqueda de estudiantes"""
        StudentService.create_student(
            dni="1234567890",
            names="Juan",
            last_names="Pérez García",
            birth_date=date(2012, 5, 15),
            section_id=self.section.id,
        )

        results = StudentService.search_students("Pérez")
        self.assertTrue(any(s.names == "Juan" for s in results))


class RepresentativeServiceTest(TestCase):
    """Tests para servicios de Representative"""

    def test_create_representative(self):
        """Probar creación de representante"""
        rep = StudentService.create_representative(
            dni="9876543210",
            names="María",
            last_names="Pérez García",
            phone="0987654321",
            email="maria@example.com",
        )

        self.assertIsNotNone(rep.id)

    def test_create_representative_duplicate_dni(self):
        """Probar que rechaza DNI duplicado"""
        StudentService.create_representative(
            dni="9876543210",
            names="María",
            last_names="Pérez",
            phone="0987654321",
        )

        with self.assertRaises(ValueError):
            StudentService.create_representative(
                dni="9876543210",
                names="Ana",
                last_names="García",
                phone="0987654322",
            )

    def test_get_representative(self):
        """Probar obtención de representante"""
        rep = StudentService.create_representative(
            dni="9876543210",
            names="María",
            last_names="Pérez",
            phone="0987654321",
        )

        retrieved = StudentService.get_representative(rep.id)
        self.assertEqual(retrieved.id, rep.id)

    def test_update_representative(self):
        """Probar actualización de representante"""
        rep = StudentService.create_representative(
            dni="9876543210",
            names="María",
            last_names="Pérez",
            phone="0987654321",
        )

        updated = StudentService.update_representative(rep.id, phone="0999999999")
        self.assertEqual(updated.phone, "0999999999")


class StudentRepresentativeServiceTest(TestCase):
    """Tests para servicios de relación Student-Representative"""

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
        self.student = StudentService.create_student(
            dni="1234567890",
            names="Juan",
            last_names="Pérez",
            birth_date=date(2012, 5, 15),
            section_id=self.section.id,
        )

    def test_assign_representative(self):
        """Probar asignación de representante"""
        rep = StudentService.create_representative(
            dni="9876543210",
            names="María",
            last_names="Pérez",
            phone="0987654321",
        )

        rel = StudentService.assign_representative(
            student_id=self.student.id, representative_id=rep.id, kinship="Madre", is_primary=True
        )

        self.assertIsNotNone(rel.id)
        self.assertTrue(rel.is_primary)

    def test_assign_representative_duplicate(self):
        """Probar que rechaza asignación duplicada"""
        rep = StudentService.create_representative(
            dni="9876543210",
            names="María",
            last_names="Pérez",
            phone="0987654321",
        )

        StudentService.assign_representative(
            student_id=self.student.id, representative_id=rep.id, kinship="Madre"
        )

        with self.assertRaises(ValueError):
            StudentService.assign_representative(
                student_id=self.student.id, representative_id=rep.id, kinship="Madre"
            )

    def test_set_primary_representative(self):
        """Probar establecimiento de representante principal"""
        rep1 = StudentService.create_representative(
            dni="1111111111",
            names="María",
            last_names="Pérez",
            phone="0987654321",
        )
        rep2 = StudentService.create_representative(
            dni="2222222222",
            names="Pedro",
            last_names="Pérez",
            phone="0987654322",
        )

        StudentService.assign_representative(self.student.id, rep1.id, kinship="Madre", is_primary=True)
        StudentService.assign_representative(self.student.id, rep2.id, kinship="Padre", is_primary=False)

        # Cambiar principal
        StudentService.set_primary_representative(self.student.id, rep2.id)

        primary = StudentService.get_primary_representative(self.student.id)
        self.assertEqual(primary.id, rep2.id)

    def test_get_contact_info(self):
        """Probar obtención de información de contacto"""
        rep = StudentService.create_representative(
            dni="9876543210",
            names="María",
            last_names="Pérez",
            phone="0987654321",
            email="maria@example.com",
        )

        StudentService.assign_representative(self.student.id, rep.id, kinship="Madre", is_primary=True)

        contact_info = StudentService.get_contact_info_for_student(self.student.id)

        self.assertIsNotNone(contact_info["primary_contact"])
        self.assertEqual(contact_info["primary_contact"]["kinship"], "Madre")
