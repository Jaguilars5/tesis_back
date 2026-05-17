from django.db import models, transaction
from apps.accounts.models import Person, User
from apps.institutions.models import DocumentType


class PersonService:
    @staticmethod
    @transaction.atomic
    def create_person_with_user(person_data, password=None, institution=None, **user_extra):
        doc_type_id = person_data.pop("document_type_id", None)
        if not doc_type_id:
            cc_type = DocumentType.objects.get_or_create(
                code="CC", defaults={"name": "Cédula de Ciudadanía"}
            )[0]
            doc_type_id = cc_type.id

        person = Person.objects.create(
            document_type_id=doc_type_id,
            **person_data,
        )
        user = User.objects.create_user(
            person=person,
            password=password,
            institution=institution,
            **user_extra,
        )
        return person, user

    @staticmethod
    @transaction.atomic
    def create_person_with_student(person_data, student_code=None):
        from apps.students.models import Student

        doc_type_id = person_data.pop("document_type_id", None)
        if not doc_type_id:
            cc_type = DocumentType.objects.get_or_create(
                code="CC", defaults={"name": "Cédula de Ciudadanía"}
            )[0]
            doc_type_id = cc_type.id

        person = Person.objects.create(
            document_type_id=doc_type_id,
            **person_data,
        )
        code = student_code or f"EST-{Student.objects.count() + 1:05d}"
        student = Student.objects.create(person=person, student_code=code)
        return person, student

    @staticmethod
    def search_person(document_number=None, email=None, names=None):
        qs = Person.objects.all()
        if document_number:
            qs = qs.filter(document_number__icontains=document_number)
        if email:
            qs = qs.filter(email__icontains=email)
        if names:
            qs = qs.filter(
                models.Q(names__icontains=names) |
                models.Q(last_names__icontains=names)
            )
        return qs
