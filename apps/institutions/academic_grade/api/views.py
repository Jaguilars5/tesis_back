from drf_spectacular.utils import extend_schema, extend_schema_view

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

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
    soft_delete=extend_schema(summary="Desactivar grado académico", tags=["institutions"]),
)
class AcademicGradeViewSet(BaseInstitutionsViewSet):
    serializer_class = AcademicGradeSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = AcademicGradeFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AcademicGradeRepository()

    def get_queryset(self):
        search = self.request.query_params.get("search")
        return self.repository.get_all(search=search)

    def perform_create(self, serializer):
        data = serializer.validated_data
        instance = AcademicGradeService.create_grade(
            name=data["name"],
            academic_sublevel_id=data.get("academic_sublevel", None),
            code=data.get("code", ""),
        )
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        instance = AcademicGradeService.update_grade(
            grade_id=serializer.instance.id,
            **data,
        )
        serializer.instance = instance
