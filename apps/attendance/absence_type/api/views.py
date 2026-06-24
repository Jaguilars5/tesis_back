from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.attendance.api.base import BaseAttendanceViewSet

from ..application.serializers import AbsenceTypeSerializer
from ..domain.services import AbsenceTypeService
from ..infrastructure.repositories import AbsenceTypeRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import AbsenceTypeFilter


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de ausencia", tags=["attendance"]),
    get=extend_schema(summary="Obtener tipo de ausencia", tags=["attendance"]),
    create=extend_schema(summary="Crear tipo de ausencia", tags=["attendance"]),
    update=extend_schema(summary="Actualizar tipo de ausencia", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar parcialmente tipo de ausencia", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar tipo de ausencia", tags=["attendance"]),
)
class AbsenceTypeViewSet(BaseAttendanceViewSet):
    serializer_class = AbsenceTypeSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = AbsenceTypeFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AbsenceTypeRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        obj = AbsenceTypeService.create_absence_type(
            code=data["code"],
            name=data["name"],
            description=data.get("description", ""),
        )
        serializer.instance = obj

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        obj = AbsenceTypeService.update_absence_type(serializer.instance.id, **data)
        serializer.instance = obj
