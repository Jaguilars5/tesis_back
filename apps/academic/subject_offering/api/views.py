from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.academic.api.base import BaseAcademicViewSet
from apps.core.utils import ok_response

from ..application.serializers import SubjectOfferingSerializer
from ..domain.services import SubjectOfferingService
from ..permissions import ACTION_PERMISSIONS
from .filters import SubjectOfferingFilter


def _raise_validation_error(exc: ValueError) -> None:
    errors = (
        exc.args[0]
        if exc.args and isinstance(exc.args[0], dict)
        else {"non_field_errors": str(exc)}
    )
    raise ValidationError(errors) from exc


@extend_schema_view(
    list=extend_schema(summary="Listar ofertas de materia", tags=["academic"]),
    get=extend_schema(summary="Obtener oferta de materia", tags=["academic"]),
    create=extend_schema(summary="Crear oferta de materia", tags=["academic"]),
    update=extend_schema(summary="Actualizar oferta de materia", tags=["academic"]),
    partial_update=extend_schema(summary="Actualizar parcialmente oferta de materia", tags=["academic"]),
    destroy=extend_schema(summary="Eliminar oferta de materia", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar oferta de materia con validaci\u00f3n de cascada", tags=["academic"]),
)
class SubjectOfferingViewSet(BaseAcademicViewSet):
    serializer_class = SubjectOfferingSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = SubjectOfferingFilter
    search_fields = [
        "subject_academic_config__subject__name",
        "section__parallel",
    ]
    ordering_fields = ["id"]
    ordering = ["-id"]

    def get_queryset(self):
        return SubjectOfferingService.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            instance = SubjectOfferingService.create_offering(
                section_id=data["section"].id,
                subject_academic_config_id=data["subject_academic_config"].id,
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        if "section" in data:
            data["section_id"] = data.pop("section").id
        if "subject_academic_config" in data:
            data["subject_academic_config_id"] = data.pop("subject_academic_config").id
        try:
            instance = SubjectOfferingService.update_offering(
                offering_id=serializer.instance.id,
                **data,
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = SubjectOfferingService.soft_delete(pk, confirm=confirm)
        return ok_response(result)
