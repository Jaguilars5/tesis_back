from drf_spectacular.utils import extend_schema, extend_schema_view

from django_filters.rest_framework import DjangoFilterBackend

from apps.academic.api.base import BaseAcademicViewSet

from ..application.serializers import SubjectOfferingSerializer
from ..domain.services import SubjectOfferingService
from ..infrastructure.repositories import SubjectOfferingRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import SubjectOfferingFilter


@extend_schema_view(
    list=extend_schema(summary="Listar ofertas de materia", tags=["academic"]),
    get=extend_schema(summary="Obtener oferta de materia", tags=["academic"]),
    create=extend_schema(summary="Crear oferta de materia", tags=["academic"]),
    update=extend_schema(summary="Actualizar oferta de materia", tags=["academic"]),
    partial_update=extend_schema(summary="Actualizar parcialmente oferta de materia", tags=["academic"]),
    destroy=extend_schema(summary="Eliminar oferta de materia", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar oferta de materia", tags=["academic"]),
)
class SubjectOfferingViewSet(BaseAcademicViewSet):
    serializer_class = SubjectOfferingSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [DjangoFilterBackend]
    filterset_class = SubjectOfferingFilter
    ordering_fields = ["id"]
    ordering = ["-id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SubjectOfferingRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        instance = SubjectOfferingService.create_offering(
            section_id=data["section"].id,
            subject_academic_config_id=data["subject_academic_config"].id,
        )
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        instance = SubjectOfferingService.update_offering(
            offering_id=serializer.instance.id,
            **data,
        )
        serializer.instance = instance
