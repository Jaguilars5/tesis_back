from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter

from apps.academic.api.base import BaseAcademicViewSet
from apps.core.utils import ok_response

from ..application.serializers import PeriodTypeSerializer
from ..domain.services import PeriodTypeService
from ..permissions import ACTION_PERMISSIONS
from .filters import PeriodTypeFilter


def _raise_validation_error(exc: ValueError) -> None:
    errors = (
        exc.args[0]
        if exc.args and isinstance(exc.args[0], dict)
        else {"non_field_errors": str(exc)}
    )
    raise ValidationError(errors) from exc


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de periodo", tags=["academic"]),
    get=extend_schema(summary="Obtener tipo de periodo", tags=["academic"]),
    create=extend_schema(summary="Crear tipo de periodo", tags=["academic"]),
    update=extend_schema(summary="Actualizar tipo de periodo", tags=["academic"]),
    partial_update=extend_schema(summary="Actualizar parcialmente tipo de periodo", tags=["academic"]),
    destroy=extend_schema(summary="Eliminar tipo de periodo", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar tipo de periodo con validaci\u00f3n de cascada", tags=["academic"]),
)
class PeriodTypeViewSet(BaseAcademicViewSet):
    serializer_class = PeriodTypeSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = PeriodTypeFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def get_queryset(self):
        return PeriodTypeService.repository.get_all(active_only=True)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            instance = PeriodTypeService.create_period_type(
                code=data["code"],
                name=data["name"],
                description=data.get("description", ""),
                divisions_per_year=data.get("divisions_per_year", 1),
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            instance = PeriodTypeService.update_period_type(
                period_type_id=serializer.instance.id,
                **data,
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = PeriodTypeService.soft_delete(pk, confirm=confirm)
        return ok_response(result)
