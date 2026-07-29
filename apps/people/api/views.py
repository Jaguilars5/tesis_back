from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter

from ..application.serializers import CitySerializer, DocumentTypeSerializer, ParishSerializer, PersonSerializer
from ..domain.services import CityService, DocumentTypeService, ParishService, PersonService
from ..permissions import CITY_ACTION_PERMISSIONS, DOCUMENT_TYPE_ACTION_PERMISSIONS, PARISH_ACTION_PERMISSIONS, PERSON_ACTION_PERMISSIONS
from .base import BasePeopleViewSet
from .filters import CityFilter, DocumentTypeFilter, ParishFilter, PersonFilter


def _raise_validation_error(exc: ValueError) -> None:
    errors = (
        exc.args[0]
        if exc.args and isinstance(exc.args[0], dict)
        else {"non_field_errors": str(exc)}
    )
    raise ValidationError(errors) from exc


@extend_schema_view(
    list=extend_schema(summary="Listar ciudades", tags=["people"]),
    get=extend_schema(summary="Obtener ciudad", tags=["people"]),
)
@extend_schema_view(
    list=extend_schema(summary="Listar parroquias", tags=["people"]),
    get=extend_schema(summary="Obtener parroquia", tags=["people"]),
    create=extend_schema(summary="Crear parroquia", tags=["people"]),
    update=extend_schema(summary="Actualizar parroquia", tags=["people"]),
    partial_update=extend_schema(summary="Actualizar parroquia parcialmente", tags=["people"]),
    destroy=extend_schema(summary="Eliminar parroquia", tags=["people"]),
)
class ParishViewSet(BasePeopleViewSet):
    serializer_class = ParishSerializer
    action_permissions = PARISH_ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = ParishFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def get_queryset(self):
        return ParishService.repository.get_all(active_only=False)

    def perform_create(self, serializer):
        data = serializer.validated_data
        if "city" in data:
            data["city_id"] = data.pop("city").id
        try:
            instance = ParishService.create_parish(
                name=data["name"],
                code=data["code"],
                parish_type=data["parish_type"],
                city_id=data["city_id"],
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        if "city" in data:
            data["city_id"] = data.pop("city").id
        try:
            instance = ParishService.update_parish(
                parish_id=serializer.instance.id,
                **data,
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance


class CityViewSet(BasePeopleViewSet):
    serializer_class = CitySerializer
    action_permissions = CITY_ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = CityFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def get_queryset(self):
        return CityService.repository.get_all(active_only=False)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            instance = CityService.create_city(
                name=data["name"],
                code=data["code"],
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            instance = CityService.update_city(
                city_id=serializer.instance.id,
                **data,
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de documento", tags=["people"]),
    get=extend_schema(summary="Obtener tipo de documento", tags=["people"]),
    create=extend_schema(summary="Crear tipo de documento", tags=["people"]),
    update=extend_schema(summary="Actualizar tipo de documento", tags=["people"]),
    partial_update=extend_schema(summary="Actualizar tipo de documento parcialmente", tags=["people"]),
    destroy=extend_schema(summary="Eliminar tipo de documento", tags=["people"]),
)
class DocumentTypeViewSet(BasePeopleViewSet):
    serializer_class = DocumentTypeSerializer
    action_permissions = DOCUMENT_TYPE_ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = DocumentTypeFilter
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name"]
    ordering = ["name"]

    def get_queryset(self):
        return DocumentTypeService.repository.get_all(active_only=False)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            instance = DocumentTypeService.create_document_type(
                code=data["code"],
                name=data["name"],
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            instance = DocumentTypeService.update_document_type(
                doc_type_id=serializer.instance.id,
                **data,
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance


@extend_schema_view(
    list=extend_schema(summary="Listar personas", tags=["people"]),
    get=extend_schema(summary="Obtener persona", tags=["people"]),
    create=extend_schema(summary="Crear persona", tags=["people"]),
    update=extend_schema(summary="Actualizar persona", tags=["people"]),
    partial_update=extend_schema(summary="Actualizar persona parcialmente", tags=["people"]),
    destroy=extend_schema(summary="Eliminar persona", tags=["people"]),
)
class PersonViewSet(BasePeopleViewSet):
    serializer_class = PersonSerializer
    action_permissions = PERSON_ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = PersonFilter
    search_fields = ["names", "last_names", "document_number", "email"]
    ordering_fields = ["names", "last_names", "document_number"]
    ordering = ["last_names", "names"]

    def get_queryset(self):
        return PersonService.repository.get_all(active_only=False)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            instance = PersonService.create_person(**data)
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            instance = PersonService.update_person(
                person_id=serializer.instance.id,
                **data,
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance
