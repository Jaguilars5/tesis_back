from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.api.permissions import HasPermission
from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.constants.permissions import people as perm

from ...repositories import CityRepository, DocumentTypeRepository
from ...repositories.person_repo import PersonRepository
from ..serializers import CitySerializer, DocumentTypeSerializer, PersonSerializer


@extend_schema_view(
    list=extend_schema(summary="Listar ciudades", tags=["people"]),
    retrieve=extend_schema(summary="Obtener ciudad", tags=["people"]),
)
class CityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CitySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CityRepository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de documento", tags=["people"]),
    retrieve=extend_schema(summary="Obtener tipo de documento", tags=["people"]),
    create=extend_schema(summary="Crear tipo de documento", tags=["people"]),
    update=extend_schema(summary="Actualizar tipo de documento", tags=["people"]),
    partial_update=extend_schema(summary="Actualizar tipo de documento parcialmente", tags=["people"]),
    destroy=extend_schema(summary="Eliminar tipo de documento", tags=["people"]),
)
class DocumentTypeViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentTypeSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_DOCUMENT_TYPE,
        "retrieve": perm.VIEW_DOCUMENT_TYPE,
        "create": perm.CREATE_DOCUMENT_TYPE,
        "update": perm.UPDATE_DOCUMENT_TYPE,
        "partial_update": perm.UPDATE_DOCUMENT_TYPE,
        "destroy": perm.DELETE_DOCUMENT_TYPE,
    }

    def get_queryset(self):
        return DocumentTypeRepository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar personas", tags=["people"]),
    retrieve=extend_schema(summary="Obtener persona", tags=["people"]),
    create=extend_schema(summary="Crear persona", tags=["people"]),
    update=extend_schema(summary="Actualizar persona", tags=["people"]),
    partial_update=extend_schema(summary="Actualizar persona parcialmente", tags=["people"]),
    destroy=extend_schema(summary="Eliminar persona", tags=["people"]),
)
class PersonViewSet(viewsets.ModelViewSet):
    serializer_class = PersonSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_PERSON,
        "retrieve": perm.VIEW_PERSON,
        "create": perm.CREATE_PERSON,
        "update": perm.UPDATE_PERSON,
        "partial_update": perm.UPDATE_PERSON,
        "destroy": perm.DELETE_PERSON,
    }

    def get_queryset(self):
        return PersonRepository.get_all()
