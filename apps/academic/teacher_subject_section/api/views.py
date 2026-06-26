from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.academic.api.base import BaseAcademicViewSet
from apps.core.utils import ok_response

from ..application.serializers import TeacherSubjectSectionSerializer
from ..domain.services import TeacherSubjectSectionService
from ..permissions import ACTION_PERMISSIONS
from .filters import TeacherSubjectSectionFilter


def _raise_validation_error(exc: ValueError) -> None:
    errors = (
        exc.args[0]
        if exc.args and isinstance(exc.args[0], dict)
        else {"non_field_errors": str(exc)}
    )
    raise ValidationError(errors) from exc


@extend_schema_view(
    list=extend_schema(summary="Listar asignaciones docente-materia", tags=["academic"]),
    get=extend_schema(summary="Obtener asignaci\u00f3n docente-materia", tags=["academic"]),
    create=extend_schema(summary="Asignar docente a materia", tags=["academic"]),
    update=extend_schema(summary="Actualizar asignaci\u00f3n docente-materia", tags=["academic"]),
    partial_update=extend_schema(summary="Actualizar parcialmente asignaci\u00f3n docente-materia", tags=["academic"]),
    destroy=extend_schema(summary="Eliminar asignaci\u00f3n docente-materia", tags=["academic"]),
    soft_delete=extend_schema(summary="Desactivar asignaci\u00f3n docente-materia con validaci\u00f3n de cascada", tags=["academic"]),
)
class TeacherSubjectSectionViewSet(BaseAcademicViewSet):
    serializer_class = TeacherSubjectSectionSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = TeacherSubjectSectionFilter
    search_fields = [
        "user__person__names",
        "user__person__last_names",
        "user__username",
        "user__email",
        "subject_offering__section__school_year__name",
        "subject_offering__section__academic_grade__name",
        "subject_offering__section__parallel",
        "subject_offering__subject_academic_config__subject__name",
    ]
    ordering_fields = ["id", "created_at", "is_active"]
    ordering = ["-id"]

    def get_queryset(self):
        return TeacherSubjectSectionService.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            instance = TeacherSubjectSectionService.assign_teacher(
                user_id=data["user"].id,
                subject_offering_id=data["subject_offering"].id,
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            instance = TeacherSubjectSectionService.update_assignment(
                assignment_id=serializer.instance.id,
                **data,
            )
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = instance

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = TeacherSubjectSectionService.soft_delete(pk, confirm=confirm)
        return ok_response(result)
