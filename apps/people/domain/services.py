from django.db import transaction

from ..application import validators
from ..infrastructure.repositories import CityRepository, DocumentTypeRepository, ParishRepository, PersonRepository


class CityService:
    repository = CityRepository

    @classmethod
    def _validate_or_raise(cls, **kwargs):
        errors = validators.run_all_validators_city(**kwargs)
        if errors:
            raise ValueError(errors)

    @classmethod
    @transaction.atomic
    def create_city(cls, name, code):
        cls._validate_or_raise(name=name, code=code)
        existing = cls.repository.first(code=code)
        if existing:
            raise ValueError({"code": "Ya existe una ciudad con este codigo"})
        return cls.repository.create(name=name, code=code)

    @classmethod
    def get_city(cls, city_id):
        obj = cls.repository.get_by_id(city_id)
        if not obj:
            raise ValueError({"id": f"Ciudad {city_id} no encontrada"})
        return obj

    @classmethod
    @transaction.atomic
    def update_city(cls, city_id, **kwargs):
        allowed = {"name", "code", "is_active"}
        obj = cls.get_city(city_id)
        cls._validate_or_raise(
            name=kwargs.get("name", obj.name),
            code=kwargs.get("code", obj.code),
        )
        if "code" in kwargs:
            existing = cls.repository.first(code=kwargs["code"])
            if existing and existing.id != city_id:
                raise ValueError({"code": "Ya existe otra ciudad con este codigo"})
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(obj.id, **clean)


class ParishService:
    repository = ParishRepository

    @classmethod
    def _validate_or_raise(cls, **kwargs):
        errors = validators.run_all_validators_parish(**kwargs)
        if errors:
            raise ValueError(errors)

    @classmethod
    @transaction.atomic
    def create_parish(cls, name, code, parish_type, city_id):
        cls._validate_or_raise(name=name, code=code, parish_type=parish_type, city_id=city_id)
        existing = cls.repository.first(code=code)
        if existing:
            raise ValueError({"code": "Ya existe una parroquia con este codigo"})
        return cls.repository.create(name=name, code=code, parish_type=parish_type, city_id=city_id)

    @classmethod
    def get_parish(cls, parish_id):
        obj = cls.repository.get_by_id(parish_id)
        if not obj:
            raise ValueError({"id": f"Parroquia {parish_id} no encontrada"})
        return obj

    @classmethod
    @transaction.atomic
    def update_parish(cls, parish_id, **kwargs):
        allowed = {"name", "code", "parish_type", "city_id", "is_active"}
        obj = cls.get_parish(parish_id)
        cls._validate_or_raise(
            name=kwargs.get("name", obj.name),
            code=kwargs.get("code", obj.code),
            parish_type=kwargs.get("parish_type", obj.parish_type),
            city_id=kwargs.get("city_id", obj.city_id),
        )
        if "code" in kwargs:
            existing = cls.repository.first(code=kwargs["code"])
            if existing and existing.id != parish_id:
                raise ValueError({"code": "Ya existe otra parroquia con este codigo"})
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(obj.id, **clean)


class DocumentTypeService:
    repository = DocumentTypeRepository

    @classmethod
    def _validate_or_raise(cls, **kwargs):
        errors = validators.run_all_validators_document_type(**kwargs)
        if errors:
            raise ValueError(errors)

    @classmethod
    @transaction.atomic
    def create_document_type(cls, code, name):
        cls._validate_or_raise(code=code, name=name)
        existing = cls.repository.first(code=code)
        if existing:
            raise ValueError({"code": "Ya existe un tipo de documento con este codigo"})
        return cls.repository.create(code=code, name=name)

    @classmethod
    def get_document_type(cls, doc_type_id):
        obj = cls.repository.get_by_id(doc_type_id)
        if not obj:
            raise ValueError({"id": f"Tipo de documento {doc_type_id} no encontrado"})
        return obj

    @classmethod
    @transaction.atomic
    def update_document_type(cls, doc_type_id, **kwargs):
        allowed = {"code", "name", "is_active"}
        obj = cls.get_document_type(doc_type_id)
        cls._validate_or_raise(
            code=kwargs.get("code", obj.code),
            name=kwargs.get("name", obj.name),
        )
        if "code" in kwargs:
            existing = cls.repository.first(code=kwargs["code"])
            if existing and existing.id != doc_type_id:
                raise ValueError({"code": "Ya existe otro tipo de documento con este codigo"})
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(obj.id, **clean)


class PersonService:
    repository = PersonRepository

    @classmethod
    def _validate_or_raise(cls, **kwargs):
        errors = validators.run_all_validators_person(**kwargs)
        if errors:
            raise ValueError(errors)

    @classmethod
    @transaction.atomic
    def create_person(cls, **data):
        cls._validate_or_raise(**data)
        existing = cls.repository.first(document_number=data.get("document_number", ""))
        if existing:
            raise ValueError({"document_number": "Ya existe una persona con este documento"})
        return cls.repository.create(**data)

    @classmethod
    def get_person(cls, person_id):
        obj = cls.repository.get_by_id(person_id)
        if not obj:
            raise ValueError({"id": f"Persona {person_id} no encontrada"})
        return obj

    @classmethod
    @transaction.atomic
    def update_person(cls, person_id, **kwargs):
        allowed = {"document_number", "names", "last_names", "birth_date", "email", "phone", "parish_id", "document_type_id", "is_active"}
        obj = cls.get_person(person_id)
        if "document_number" in kwargs:
            existing = cls.repository.first(document_number=kwargs["document_number"])
            if existing and existing.id != person_id:
                raise ValueError({"document_number": "Ya existe otra persona con este documento"})
        clean = {k: v for k, v in kwargs.items() if k in allowed}
        return cls.repository.update(obj.id, **clean)

    @classmethod
    @transaction.atomic
    def create_person_with_user(cls, person_data, password=None, **user_extra):
        from apps.iam.models import User

        doc_type_id = person_data.pop("document_type_id", None)
        if not doc_type_id:
            from ..infrastructure.models import DocumentType
            cc_type = DocumentType.objects.get_or_create(code="CC", defaults={"name": "Cedula de Ciudadania"})[0]
            doc_type_id = cc_type.id

        person = cls.repository.create(document_type_id=doc_type_id, **person_data)
        user = User.objects.create_user(person=person, password=password, **user_extra)
        return person, user

    @classmethod
    @transaction.atomic
    def create_person_with_student(cls, person_data, student_code=None):
        from apps.students.models import Student

        doc_type_id = person_data.pop("document_type_id", None)
        if not doc_type_id:
            from ..infrastructure.models import DocumentType
            cc_type = DocumentType.objects.get_or_create(code="CC", defaults={"name": "Cedula de Ciudadania"})[0]
            doc_type_id = cc_type.id

        person = cls.repository.create(document_type_id=doc_type_id, **person_data)
        code = student_code or f"EST-{Student.objects.count() + 1:05d}"
        student = Student.objects.create(person=person, student_code=code)
        return person, student

    @classmethod
    def search_person(cls, document_number=None, email=None, names=None):
        qs = cls.repository.get_all()
        if document_number:
            qs = qs.filter(document_number__icontains=document_number)
        if email:
            qs = qs.filter(email__icontains=email)
        if names:
            from django.db import models as db_models
            qs = qs.filter(db_models.Q(names__icontains=names) | db_models.Q(last_names__icontains=names))
        return qs
