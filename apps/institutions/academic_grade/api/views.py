from drf_spectacular.utils import extend_schema, extend_schema_view

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.utils import ok_response
from apps.institutions.api.base import BaseInstitutionsViewSet

from ..application.serializers import AcademicGradeSerializer
from ..domain.services import AcademicGradeService
from ..infrastructure.repositories import AcademicGradeRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import AcademicGradeFilter


@extend_schema_view(
    list=extend_schema(summary="Listar grados académicos", tags=["institutions"]),
    get=extend_schema(summary="Obtener grado académico", tags=["institutions"]),
    create=extend_schema(summary="Crear grado académico", tags=["institutions"]),
    update=extend_schema(summary="Actualizar grado académico", tags=["institutions"]),
    destroy=extend_schema(summary="Eliminar grado académico", tags=["institutions"]),
    soft_delete=extend_schema(summary="Desactivar grado académico con cascada", tags=["institutions"]),
)
class AcademicGradeViewSet(BaseInstitutionsViewSet):
    serializer_class = AcademicGradeSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = AcademicGradeFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AcademicGradeRepository()

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = AcademicGradeService.soft_delete(pk, confirm=confirm)
        return ok_response(result)

    def get_queryset(self):
        return self.repository.get_all(active_only=False)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            sublevel = data.get("academic_sublevel")
            instance = AcademicGradeService.create_grade(
                name=data["name"],
                academic_sublevel_id=sublevel.id if sublevel else None,
                code=data.get("code", ""),
            )
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            clean = dict(data)
            sublevel = clean.pop("academic_sublevel", None)
            if sublevel is not None:
                clean["academic_sublevel_id"] = sublevel.id
            instance = AcademicGradeService.update_grade(
                grade_id=serializer.instance.id,
                **clean,
            )
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))
        serializer.instance = instance
