from drf_spectacular.utils import extend_schema, extend_schema_view

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from apps.academic.api.base import BaseAcademicViewSet

from ..application.serializers import SubjectSerializer
from ..domain.services import SubjectService
from ..infrastructure.repositories import SubjectRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import SubjectFilter


@extend_schema_view(
    list=extend_schema(summary="Listar materias", tags=["academic"]),
    get=extend_schema(summary="Obtener materia", tags=["academic"]),
    create=extend_schema(summary="Crear materia", tags=["academic"]),
    update=extend_schema(summary="Actualizar materia", tags=["academic"]),
    partial_update=extend_schema(summary="Actualizar parcialmente materia", tags=["academic"]),
    destroy=extend_schema(summary="Eliminar materia", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar materia", tags=["academic"]),
)
class SubjectViewSet(BaseAcademicViewSet):
    serializer_class = SubjectSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = SubjectFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SubjectRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        instance = SubjectService.create_subject(
            name=data["name"],
            code=data["code"],
        )
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        instance = SubjectService.update_subject(
            subject_id=serializer.instance.id,
            **data,
        )
        serializer.instance = instance
