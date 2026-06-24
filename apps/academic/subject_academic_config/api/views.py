from drf_spectacular.utils import extend_schema, extend_schema_view

from django_filters.rest_framework import DjangoFilterBackend

from apps.academic.api.base import BaseAcademicViewSet

from ..application.serializers import SubjectAcademicConfigSerializer
from ..domain.services import SubjectAcademicConfigService
from ..infrastructure.repositories import SubjectAcademicConfigRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import SubjectAcademicConfigFilter


@extend_schema_view(
    list=extend_schema(summary="Listar configuraciones materia-grado", tags=["academic"]),
    get=extend_schema(summary="Obtener configuración materia-grado", tags=["academic"]),
    create=extend_schema(summary="Crear configuración materia-grado", tags=["academic"]),
    update=extend_schema(summary="Actualizar configuración materia-grado", tags=["academic"]),
    partial_update=extend_schema(summary="Actualizar parcialmente configuración materia-grado", tags=["academic"]),
    destroy=extend_schema(summary="Eliminar configuración materia-grado", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar configuración materia-grado", tags=["academic"]),
)
class SubjectAcademicConfigViewSet(BaseAcademicViewSet):
    serializer_class = SubjectAcademicConfigSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [DjangoFilterBackend]
    filterset_class = SubjectAcademicConfigFilter
    ordering_fields = ["weekly_hours"]
    ordering = ["subject"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SubjectAcademicConfigRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        instance = SubjectAcademicConfigService.create_config(
            subject_id=data["subject"].id,
            academic_grade_id=data["academic_grade"].id,
            weekly_hours=data["weekly_hours"],
            is_required=data.get("is_required", True),
        )
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        instance = SubjectAcademicConfigService.update_config(
            config_id=serializer.instance.id,
            **data,
        )
        serializer.instance = instance
