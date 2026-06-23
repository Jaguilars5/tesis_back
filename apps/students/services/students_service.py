from datetime import date, datetime
from django.db import models, transaction
from apps.iam.models import User, UserRole
from apps.iam.models.role import Role
from apps.people.models import Person, DocumentType
from ..models import Kinship, Student, StudentRepresentative
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
        email="", phone="", document_type_id=None, city_id=None,
        has_special_needs=False, special_needs_type_id=None,
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
            city_id=city_id,
        )
        username = User.generate_username(names, last_names) or document_number
        user = User.objects.create_user(
            person=person,
            username=username,
            password=document_number,
            must_change_password=True,
        )
        role, _ = Role.objects.get_or_create(
            code="ESTUDIANTE", defaults={"name": "Estudiante"}
        )
        UserRole.objects.create(user=user, role=role)
        code = f"EST-{StudentRepository.count() + 1:05d}"
        student_data = {"user": user, "student_code": code}
        if has_special_needs:
            student_data["has_special_needs"] = True
            if special_needs_type_id:
                student_data["special_needs_type_id"] = special_needs_type_id
        student = StudentRepository.create(**student_data)
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
    def create_and_assign_representative(
        student_id, document_number, names, last_names,
        email="", phone="", birth_date=None, document_type_id=None,
        city_id=None, kinship="Padre", **kwargs
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
            city_id=city_id,
        )
        username = User.generate_username(names, last_names) or document_number
        user = User.objects.create_user(
            person=person,
            username=username,
            password=document_number,
            must_change_password=True,
        )
        role, _ = Role.objects.get_or_create(
            code="REPRESENTANTE", defaults={"name": "Representante"}
        )
        UserRole.objects.create(user=user, role=role)
        return StudentService.assign_representative(
            student_id=student_id, user_id=user.id, kinship=kinship, **kwargs
        )

    @staticmethod
    def assign_representative(student_id, user_id, kinship="Padre", **kwargs):
        if isinstance(kinship, str):
            kinship_obj, _ = Kinship.objects.get_or_create(
                code=kinship.upper() if len(kinship) <= 30 else "OTRO",
                defaults={"name": kinship}
            )
        else:
            kinship_obj = kinship
        rel = StudentRepresentative(
            student_id=student_id,
            user_id=user_id,
            kinship=kinship_obj,
            **kwargs
        )
        rel.save()
        return rel

    @staticmethod
    def remove_representative(student_id, user_id):
        rel = StudentRepresentativeRepository.get_relationship(student_id, user_id)
        if not rel:
            raise ValueError("Relación no encontrada")
        rel.delete()
        return True

    @staticmethod
    def set_primary_representative(student_id, user_id):
        StudentRepresentativeRepository.get_relationship(student_id, user_id)
        StudentRepresentative.objects.filter(
            student_id=student_id, is_primary=True
        ).update(is_primary=False)
        StudentRepresentative.objects.filter(
            student_id=student_id, user_id=user_id
        ).update(is_primary=True)
