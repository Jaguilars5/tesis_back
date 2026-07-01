from drf_spectacular.utils import extend_schema, extend_schema_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.utils import ok_response
from apps.institutions.api.base import BaseInstitutionsViewSet

from ..application.serializers import AcademicLevelSerializer
from ..domain.services import AcademicLevelService
from ..infrastructure.repositories import AcademicLevelRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import AcademicLevelFilter


@extend_schema_view(
    list=extend_schema(summary="Listar niveles academicos", tags=["institutions"]),
    get=extend_schema(summary="Obtener nivel academico", tags=["institutions"]),
    create=extend_schema(summary="Crear nivel academico", tags=["institutions"]),
    update=extend_schema(summary="Actualizar nivel academico", tags=["institutions"]),
    partial_update=extend_schema(summary="Actualizar nivel parcialmente", tags=["institutions"]),
    destroy=extend_schema(summary="Eliminar nivel academico", tags=["institutions"]),
    soft_delete=extend_schema(summary="Desactivar nivel académico con cascada", tags=["institutions"]),
)
class AcademicLevelViewSet(BaseInstitutionsViewSet):
    serializer_class = AcademicLevelSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = AcademicLevelFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AcademicLevelRepository()

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = AcademicLevelService.soft_delete(pk, confirm=confirm)
        return ok_response(result)

    def get_queryset(self):
        return self.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            obj = AcademicLevelService.create_academic_level(
                name=data["name"],
                code=data.get("code", ""),
                description=data.get("description", ""),
            )
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))
        serializer.instance = obj

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        try:
            obj = AcademicLevelService.update_academic_level(serializer.instance.id, **data)
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))
        serializer.instance = obj
