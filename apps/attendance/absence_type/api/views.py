from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.attendance.api.base import BaseAttendanceViewSet
from apps.core.utils import ok_response

from ..application.serializers import AbsenceTypeSerializer
from ..domain.services import AbsenceTypeService
from ..permissions import ACTION_PERMISSIONS
from .filters import AbsenceTypeFilter


def _raise_validation_error(exc: ValueError) -> None:
    errors = (
        exc.args[0]
        if exc.args and isinstance(exc.args[0], dict)
        else {"non_field_errors": str(exc)}
    )
    raise ValidationError(errors) from exc


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de ausencia", tags=["attendance"]),
    get=extend_schema(summary="Obtener tipo de ausencia", tags=["attendance"]),
    create=extend_schema(summary="Crear tipo de ausencia", tags=["attendance"]),
    update=extend_schema(summary="Actualizar tipo de ausencia", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar parcialmente tipo de ausencia", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar tipo de ausencia", tags=["attendance"]),
    soft_delete=extend_schema(summary="Desactivar tipo de ausencia con validación de cascada", tags=["attendance"]),
)
class AbsenceTypeViewSet(BaseAttendanceViewSet):
    serializer_class = AbsenceTypeSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = AbsenceTypeFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def get_queryset(self):
        return AbsenceTypeService.repository.get_all(active_only=False)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            obj = AbsenceTypeService.create_absence_type(
                code=data["code"],
                name=data["name"],
                description=data.get("description", ""),
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = obj

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        try:
            obj = AbsenceTypeService.update_absence_type(
                serializer.instance.id, **data
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = obj

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = AbsenceTypeService.soft_delete(pk, confirm=confirm)
        return ok_response(result)
