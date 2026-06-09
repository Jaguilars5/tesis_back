from datetime import date, datetime
from django.db import models, transaction
from apps.people.models import Person, DocumentType
from ..models import Student, StudentRepresentative
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
        code = f"EST-{StudentRepository.count() + 1:05d}"
        student = StudentRepository.create(person=person, student_code=code)
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
        return StudentRepository.get_by_section(section_id)

    @staticmethod
    def search_students(query):
        return StudentRepository.search(query)

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
        student.is_active = False
        student.save()
        return student

    @staticmethod
    def assign_representative(student_id, person_id, kinship="Padre", **kwargs):
        rel = StudentRepresentative(
            student_id=student_id,
            person_id=person_id,
            kinship=kinship,
            **kwargs
        )
        rel.save()
        return rel

    @staticmethod
    def remove_representative(student_id, person_id):
        rel = StudentRepresentativeRepository.get_relationship(student_id, person_id)
        if not rel:
            raise ValueError("Relación no encontrada")
        rel.delete()
        return True

    @staticmethod
    def set_primary_representative(student_id, person_id):
        StudentRepresentativeRepository.get_relationship(student_id, person_id)
        StudentRepresentative.objects.filter(
            student_id=student_id, is_primary=True
        ).update(is_primary=False)
        StudentRepresentative.objects.filter(
            student_id=student_id, person_id=person_id
        ).update(is_primary=True)
