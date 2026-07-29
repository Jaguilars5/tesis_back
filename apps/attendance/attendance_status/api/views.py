from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.attendance.api.base import BaseAttendanceViewSet

from ..application.serializers import AttendanceStatusSerializer
from ..domain.services import AttendanceStatusService
from ..infrastructure.repositories import AttendanceStatusRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import AttendanceStatusFilter


@extend_schema_view(
    list=extend_schema(summary="Listar estados de asistencia", tags=["attendance"]),
    get=extend_schema(summary="Obtener estado de asistencia", tags=["attendance"]),
    create=extend_schema(summary="Crear estado de asistencia", tags=["attendance"]),
    update=extend_schema(summary="Actualizar estado de asistencia", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar parcialmente estado de asistencia", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar estado de asistencia", tags=["attendance"]),
    soft_delete=extend_schema(summary="Desactivar estado de asistencia", tags=["attendance"]),
)
class AttendanceStatusViewSet(BaseAttendanceViewSet):
    serializer_class = AttendanceStatusSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = AttendanceStatusFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def get_queryset(self):
        return AttendanceStatusRepository.get_all(active_only=False)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            obj = AttendanceStatusService.create_attendance_status(
                code=data["code"],
                name=data["name"],
                description=data.get("description", ""),
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            obj = AttendanceStatusService.update_attendance_status(
                serializer.instance.id,
                code=data.get("code"),
                name=data.get("name"),
                description=data.get("description", ""),
                is_active=data.get("is_active"),
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))
