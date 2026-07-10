from apps.core.repositories.base import BaseRepository
from ..domain.repositories import CityRepositoryInterface, DocumentTypeRepositoryInterface, ParishRepositoryInterface, PersonRepositoryInterface
from .models import City, DocumentType, Parish, Person


class CityRepository(BaseRepository, CityRepositoryInterface):
    model = City

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")


class DocumentTypeRepository(BaseRepository, DocumentTypeRepositoryInterface):
    model = DocumentType

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")


class ParishRepository(BaseRepository, ParishRepositoryInterface):
    model = Parish

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("name")

    @classmethod
    def get_by_code(cls, code):
        return cls.first(code=code)

    @classmethod
    def get_by_city(cls, city_id):
        return cls.model.objects.filter(city_id=city_id, is_active=True).order_by("name")


class PersonRepository(BaseRepository, PersonRepositoryInterface):
    model = Person

    @classmethod
    def get_all(cls, active_only=True):
        return super().get_all(active_only=active_only).order_by("last_names", "names")

    @classmethod
    def get_by_document_number(cls, doc_number):
        return cls.first(document_number=doc_number)

    @classmethod
    def search(cls, query):
        from django.db import models as db_models
        return cls.model.objects.filter(
            db_models.Q(names__icontains=query) |
            db_models.Q(last_names__icontains=query) |
            db_models.Q(document_number__icontains=query) |
            db_models.Q(email__icontains=query)
        )

    @classmethod
    def get_by_email(cls, email):
        return cls.first(email__iexact=email)
