from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.academic.api.base import BaseAcademicViewSet
from apps.core.utils import ok_response

from ..application.serializers import SubjectSerializer
from ..domain.services import SubjectService
from ..permissions import ACTION_PERMISSIONS
from .filters import SubjectFilter


def _raise_validation_error(exc: ValueError) -> None:
    errors = (
        exc.args[0]
        if exc.args and isinstance(exc.args[0], dict)
        else {"non_field_errors": str(exc)}
    )
    raise ValidationError(errors) from exc


@extend_schema_view(
    list=extend_schema(summary="Listar materias", tags=["academic"]),
    get=extend_schema(summary="Obtener materia", tags=["academic"]),
    create=extend_schema(summary="Crear materia", tags=["academic"]),
    update=extend_schema(summary="Actualizar materia", tags=["academic"]),
    partial_update=extend_schema(summary="Actualizar parcialmente materia", tags=["academic"]),
    destroy=extend_schema(summary="Eliminar materia", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar materia con validaci\u00f3n de cascada", tags=["academic"]),
)
class SubjectViewSet(BaseAcademicViewSet):
    serializer_class = SubjectSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = SubjectFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def get_queryset(self):
        return SubjectService.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            instance = SubjectService.create_subject(
                name=data["name"],
                code=data["code"],
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            instance = SubjectService.update_subject(
                subject_id=serializer.instance.id,
                **data,
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = SubjectService.soft_delete(pk, confirm=confirm)
        return ok_response(result)
