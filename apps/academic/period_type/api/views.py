from drf_spectacular.utils import extend_schema, extend_schema_view

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from apps.academic.api.base import BaseAcademicViewSet

from ..application.serializers import PeriodTypeSerializer
from ..domain.services import PeriodTypeService
from ..infrastructure.repositories import PeriodTypeRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import PeriodTypeFilter


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de período", tags=["academic"]),
    get=extend_schema(summary="Obtener tipo de período", tags=["academic"]),
    create=extend_schema(summary="Crear tipo de período", tags=["academic"]),
    update=extend_schema(summary="Actualizar tipo de período", tags=["academic"]),
    partial_update=extend_schema(summary="Actualizar parcialmente tipo de período", tags=["academic"]),
    destroy=extend_schema(summary="Eliminar tipo de período", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar tipo de período", tags=["academic"]),
)
class PeriodTypeViewSet(BaseAcademicViewSet):
    serializer_class = PeriodTypeSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = PeriodTypeFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = PeriodTypeRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        instance = PeriodTypeService.create_period_type(
            code=data["code"],
            name=data["name"],
            description=data.get("description", ""),
            divisions_per_year=data.get("divisions_per_year", 1),
        )
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        instance = PeriodTypeService.update_period_type(
            period_type_id=serializer.instance.id,
            **data,
        )
        serializer.instance = instance
