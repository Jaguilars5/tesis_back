from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.academic.api.base import BaseAcademicViewSet

from ..application.serializers import AcademicPeriodSerializer
from ..domain.services import AcademicPeriodService
from ..infrastructure.repositories import AcademicPeriodRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import AcademicPeriodFilter


def _raise_validation_error(exc: ValueError) -> None:
    errors = (
        exc.args[0]
        if exc.args and isinstance(exc.args[0], dict)
        else {"non_field_errors": str(exc)}
    )
    raise ValidationError(errors) from exc


@extend_schema_view(
    list=extend_schema(summary="Listar periodos académicos", tags=["academic"]),
    get=extend_schema(summary="Obtener periodo académico", tags=["academic"]),
    create=extend_schema(summary="Crear periodo académico", tags=["academic"]),
    update=extend_schema(summary="Actualizar periodo académico", tags=["academic"]),
    partial_update=extend_schema(summary="Actualizar parcialmente periodo académico", tags=["academic"]),
    destroy=extend_schema(summary="Eliminar periodo académico", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar periodo académico", tags=["academic"]),
)
class AcademicPeriodViewSet(BaseAcademicViewSet):
    serializer_class = AcademicPeriodSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = AcademicPeriodFilter
    search_fields = ["name", "code"]
    ordering_fields = ["start_date", "end_date", "name", "year_weight"]
    ordering = ["-start_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AcademicPeriodRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            period = AcademicPeriodService.create_academic_period(
                name=data["name"],
                school_year_id=data["school_year"].id
                if hasattr(data["school_year"], "id")
                else data["school_year"],
                period_type=data.get("period_type"),
                start_date=data["start_date"],
                end_date=data["end_date"],
                is_regular_period=data.get("is_regular_period", True),
                year_weight=data.get("year_weight"),
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = period

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        if "period_type" in data and data["period_type"] is not None:
            data["period_type_id"] = data.pop("period_type").pk
        elif "period_type" in data:
            data.pop("period_type")
        try:
            period = AcademicPeriodService.update_academic_period(
                serializer.instance.id,
                **data,
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = period
