from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter

from apps.academic.api.base import BaseAcademicViewSet
from apps.core.utils import ok_response

from ..application.serializers import SubjectAcademicConfigSerializer
from ..domain.services import SubjectAcademicConfigService
from ..permissions import ACTION_PERMISSIONS
from .filters import SubjectAcademicConfigFilter


def _raise_validation_error(exc: ValueError) -> None:
    errors = (
        exc.args[0]
        if exc.args and isinstance(exc.args[0], dict)
        else {"non_field_errors": str(exc)}
    )
    raise ValidationError(errors) from exc


@extend_schema_view(
    list=extend_schema(summary="Listar configuraciones materia-grado", tags=["academic"]),
    get=extend_schema(summary="Obtener configuraci\u00f3n materia-grado", tags=["academic"]),
    create=extend_schema(summary="Crear configuraci\u00f3n materia-grado", tags=["academic"]),
    update=extend_schema(summary="Actualizar configuraci\u00f3n materia-grado", tags=["academic"]),
    partial_update=extend_schema(summary="Actualizar parcialmente configuraci\u00f3n materia-grado", tags=["academic"]),
    destroy=extend_schema(summary="Eliminar configuraci\u00f3n materia-grado", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar configuraci\u00f3n materia-grado con validaci\u00f3n de cascada", tags=["academic"]),
)
class SubjectAcademicConfigViewSet(BaseAcademicViewSet):
    serializer_class = SubjectAcademicConfigSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = SubjectAcademicConfigFilter
    ordering_fields = ["weekly_hours"]
    ordering = ["subject"]

    def get_queryset(self):
        return SubjectAcademicConfigService.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            instance = SubjectAcademicConfigService.create_config(
                subject_id=data["subject"].id,
                academic_grade_id=data["academic_grade"].id,
                weekly_hours=data["weekly_hours"],
                is_required=data.get("is_required", True),
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            instance = SubjectAcademicConfigService.update_config(
                config_id=serializer.instance.id,
                **data,
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = SubjectAcademicConfigService.soft_delete(pk, confirm=confirm)
        return ok_response(result)
