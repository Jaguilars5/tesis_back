from datetime import date, datetime
from django.db import models, transaction
from apps.accounts.models import Person
from apps.institutions.models import DocumentType
from ..models import Student, Student_Representative
from ..repositories.students_repo import (
    StudentRepository,
    StudentRepresentativeRepository,
)


class StudentService:
    @staticmethod
    def _parse_date(value):
        if value is None or isinstance(value, date):
            return value
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
        return value

    @staticmethod
    def create_student(
        document_number, names, last_names, birth_date=None,
        email="", phone="", document_type_id=None,
    ):
        if not document_type_id:
            cc_type = DocumentType.objects.get_or_create(
                code="CC", defaults={"name": "Cédula de Ciudadanía"}
            )[0]
            document_type_id = cc_type.id

        person = Person.objects.create(
            document_type_id=document_type_id,
            document_number=document_number,
            names=names,
            last_names=last_names,
            birth_date=StudentService._parse_date(birth_date),
            email=email,
            phone=phone,
        )
        code = f"EST-{Student.objects.count() + 1:05d}"
        student = Student(person=person, student_code=code)
        student.save()
        return student

    @staticmethod
    def get_student(student_id):
        student = StudentRepository.get_by_id(student_id)
        if not student:
            raise ValueError(f"Estudiante {student_id} no encontrado")
        return student

    @staticmethod
    def get_all_students():
        return StudentRepository.get_all()

    @staticmethod
    def list_students_by_section(section_id):
        return Student.objects.none()

    @staticmethod
    def search_students(query):
        return Student.objects.filter(
            models.Q(person__names__icontains=query) |
            models.Q(person__last_names__icontains=query) |
            models.Q(person__document_number__icontains=query) |
            models.Q(student_code__icontains=query)
        ).distinct()

    @staticmethod
    def update_student(student_id, **kwargs):
        student = StudentService.get_student(student_id)
        for key, value in kwargs.items():
            if hasattr(student, key):
                setattr(student, key, value)
        student.save()
        return student

    @staticmethod
    def deactivate_student(student_id):
        student = StudentService.get_student(student_id)
        student.active = False
        student.save()
        return student

    @staticmethod
    def assign_representative(student_id, person_id, kinship="Padre", **kwargs):
        rel = Student_Representative(
            student_id=student_id,
            person_id=person_id,
            kinship=kinship,
            **kwargs
        )
        rel.save()
        return rel

    @staticmethod
    def remove_representative(student_id, person_id):
        rel = Student_Representative.objects.filter(
            student_id=student_id, person_id=person_id
        ).first()
        if not rel:
            raise ValueError("Relación no encontrada")
        rel.delete()
        return True

    @staticmethod
    def set_primary_representative(student_id, person_id):
        Student_Representative.objects.filter(
            student_id=student_id, is_primary=True
        ).update(is_primary=False)
        Student_Representative.objects.filter(
            student_id=student_id, person_id=person_id
        ).update(is_primary=True)
