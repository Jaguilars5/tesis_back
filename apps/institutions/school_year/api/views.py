from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.utils import ok_response
from apps.institutions.api.base import BaseInstitutionsViewSet

from ..application.serializers import SchoolYearSerializer
from ..domain.services import SchoolYearService
from ..infrastructure.repositories import SchoolYearRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import SchoolYearFilter


def _raise_validation_error(exc: ValueError) -> None:
    errors = (
        exc.args[0]
        if exc.args and isinstance(exc.args[0], dict)
        else {"non_field_errors": str(exc)}
    )
    raise ValidationError(errors) from exc


@extend_schema_view(
    list=extend_schema(summary="Listar años escolares", tags=["institutions"]),
    get=extend_schema(summary="Obtener año escolar", tags=["institutions"]),
    create=extend_schema(summary="Crear año escolar", tags=["institutions"]),
    update=extend_schema(summary="Actualizar año escolar", tags=["institutions"]),
    partial_update=extend_schema(summary="Actualizar año escolar parcialmente", tags=["institutions"]),
    destroy=extend_schema(summary="Eliminar año escolar", tags=["institutions"]),
    soft_delete=extend_schema(summary="Desactivar año escolar con cascada", tags=["institutions"]),
)
class SchoolYearViewSet(BaseInstitutionsViewSet):
    serializer_class = SchoolYearSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = SchoolYearFilter
    search_fields = ["start_date", "end_date"]
    ordering_fields = ["start_date", "end_date"]
    ordering = ["-start_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SchoolYearRepository()

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = SchoolYearService.soft_delete(pk, confirm=confirm)
        return ok_response(result)

    def get_queryset(self):
        return self.repository.get_all(active_only=False)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            obj = SchoolYearService.create_school_year(
                start_date=data["start_date"],
                end_date=data["end_date"],
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = obj

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        try:
            obj = SchoolYearService.update_school_year(serializer.instance.id, **data)
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = obj

