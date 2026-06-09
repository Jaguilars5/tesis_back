from datetime import date

from django.test import TestCase

from apps.people.models import Person
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.institutions.models import AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section
from apps.students.models import Enrollment, EnrollmentStatus, Student, StudentRepresentative
from apps.students.repositories.enrollment_repo import EnrollmentRepository
from apps.students.repositories.students_repo import StudentRepresentativeRepository, StudentRepository


class StudentsRepositoryTest(TestCase):
    """Tests para los repositorios del módulo students."""

    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            name="2025", start_date=date(2025, 1, 1), end_date=date(2025, 12, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Primaria")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, code="BASICA", name="Básica"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel, name="7", sequence_order=1,
        )
        self.section = Section.objects.create(
            school_year=self.school_year, academic_grade=self.academic_grade,
            parallel="A", capacity=30,
        )
        self.student = create_test_student(
            document_number="0912345678", names="Juan", last_names="Lopez",
            birth_date=date(2010, 1, 1), student_code="EST-001",
        )
        self.student2 = create_test_student(
            document_number="0987654321", names="Maria", last_names="Garcia",
            birth_date=date(2011, 5, 10), student_code="EST-002",
        )
        self.status, _ = EnrollmentStatus.objects.get_or_create(
            code="ACT", defaults={"name": "Activa"},
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student, section=self.section,
            enrollment_status=self.status,
        )
        self.user = create_test_user(
            email="rep@test.com", dni="0102030405",
            names="Carlos", last_names="Padre",
        )

    # --- StudentRepository ---

    def test_student_create(self):
        from apps.people.models import DocumentType
        doc_type = DocumentType.objects.get_or_create(
            code="CC", defaults={"name": "Cédula de Ciudadanía"},
        )[0]
        new_person = Person.objects.create(
            document_type=doc_type, document_number="1234567890",
            names="Nuevo", last_names="Estudiante", email="nuevo@test.com",
        )
        obj = StudentRepository.create(
            student_code="EST-003",
            person=new_person,
        )
        self.assertEqual(obj.student_code, "EST-003")

    def test_student_get_by_id(self):
        result = StudentRepository.get_by_id(self.student.pk)
        self.assertEqual(result.student_code, "EST-001")

    def test_student_get_all(self):
        results = StudentRepository.get_all(active_only=False)
        self.assertEqual(results.count(), 2)

    def test_student_update(self):
        updated = StudentRepository.update(self.student.pk, residential_zone="Urbana")
        self.assertEqual(updated.residential_zone, "Urbana")

    def test_student_delete(self):
        pk = self.student2.pk
        StudentRepository.delete(pk)
        self.assertFalse(Student.objects.filter(pk=pk).exists())

    def test_student_exists(self):
        self.assertTrue(StudentRepository.exists(pk=self.student.pk))
        self.assertFalse(StudentRepository.exists(pk=99999))

    def test_student_get_by_dni(self):
        result = StudentRepository.get_by_dni("0912345678")
        self.assertEqual(result.student_code, "EST-001")

    def test_student_get_by_dni_not_found(self):
        result = StudentRepository.get_by_dni("0000000000")
        self.assertIsNone(result)

    def test_student_get_by_section(self):
        results = StudentRepository.get_by_section(self.section.pk)
        self.assertEqual(results.count(), 1)

    def test_student_search_by_name(self):
        results = StudentRepository.search("Juan")
        self.assertEqual(results.count(), 1)

    def test_student_search_by_code(self):
        results = StudentRepository.search("EST-001")
        self.assertEqual(results.count(), 1)

    def test_student_search_no_results(self):
        results = StudentRepository.search("NoExiste")
        self.assertEqual(results.count(), 0)

    # --- StudentRepresentativeRepository ---

    def test_representative_create(self):
        obj = StudentRepresentativeRepository.create(
            student=self.student, person=self.user.person,
            kinship="Padre", is_primary=True,
        )
        self.assertEqual(obj.kinship, "Padre")
        self.assertTrue(obj.is_primary)

    def test_representative_get_by_id(self):
        rep = StudentRepresentative.objects.create(
            student=self.student, person=self.user.person, kinship="Padre",
        )
        result = StudentRepresentativeRepository.get_by_id(rep.pk)
        self.assertEqual(result.kinship, "Padre")

    def test_representative_get_by_student(self):
        StudentRepresentative.objects.create(
            student=self.student, person=self.user.person, kinship="Padre",
        )
        results = StudentRepresentativeRepository.get_by_student(self.student.pk)
        self.assertEqual(results.count(), 1)

    def test_representative_get_by_person(self):
        StudentRepresentative.objects.create(
            student=self.student, person=self.user.person, kinship="Padre",
        )
        results = StudentRepresentativeRepository.get_by_person(self.user.person.pk)
        self.assertEqual(results.count(), 1)

    def test_representative_get_relationship(self):
        StudentRepresentative.objects.create(
            student=self.student, person=self.user.person, kinship="Padre",
        )
        result = StudentRepresentativeRepository.get_relationship(
            self.student.pk, self.user.person.pk,
        )
        self.assertIsNotNone(result)

    def test_representative_get_relationship_not_found(self):
        result = StudentRepresentativeRepository.get_relationship(99999, 99999)
        self.assertIsNone(result)

    def test_representative_delete(self):
        rep = StudentRepresentative.objects.create(
            student=self.student, person=self.user.person, kinship="Madre",
        )
        pk = rep.pk
        StudentRepresentativeRepository.delete(pk)
        self.assertFalse(StudentRepresentative.objects.filter(pk=pk).exists())

    # --- EnrollmentRepository (standalone staticmethods) ---

    def test_enrollment_get_active_by_student(self):
        result = EnrollmentRepository.get_active_by_student(self.student)
        self.assertEqual(result.pk, self.enrollment.pk)

    def test_enrollment_get_by_section(self):
        results = EnrollmentRepository.get_by_section(self.section)
        self.assertEqual(results.count(), 1)

    def test_enrollment_get_by_section_with_status(self):
        results = EnrollmentRepository.get_by_section(self.section, status_code="ACT")
        self.assertEqual(results.count(), 1)

    def test_enrollment_get_by_school_year(self):
        results = EnrollmentRepository.get_by_school_year(self.school_year)
        self.assertEqual(results.count(), 1)

    def test_enrollment_get_students_by_section(self):
        results = EnrollmentRepository.get_students_by_section(self.section)
        self.assertEqual(results.count(), 1)

    def test_enrollment_count_active_in_section(self):
        count = EnrollmentRepository.count_active_in_section(self.section)
        self.assertEqual(count, 1)

    def test_enrollment_has_active_enrollment_true(self):
        self.assertTrue(
            EnrollmentRepository.has_active_enrollment(self.student)
        )

    def test_enrollment_has_active_enrollment_false(self):
        self.assertFalse(
            EnrollmentRepository.has_active_enrollment(self.student2)
        )
