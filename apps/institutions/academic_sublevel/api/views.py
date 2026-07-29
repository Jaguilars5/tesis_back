from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.utils import ok_response
from apps.institutions.api.base import BaseInstitutionsViewSet

from ..application.serializers import AcademicSublevelSerializer
from ..domain.services import AcademicSublevelService
from ..infrastructure.repositories import AcademicSublevelRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import AcademicSublevelFilter


@extend_schema_view(
    list=extend_schema(summary="Listar subniveles academicos", tags=["institutions"]),
    get=extend_schema(summary="Obtener subnivel academico", tags=["institutions"]),
    create=extend_schema(summary="Crear subnivel academico", tags=["institutions"]),
    update=extend_schema(summary="Actualizar subnivel academico", tags=["institutions"]),
    partial_update=extend_schema(summary="Actualizar subnivel parcialmente", tags=["institutions"]),
    destroy=extend_schema(summary="Eliminar subnivel academico", tags=["institutions"]),
    soft_delete=extend_schema(summary="Desactivar subnivel académico con cascada", tags=["institutions"]),
)
class AcademicSublevelViewSet(BaseInstitutionsViewSet):
    serializer_class = AcademicSublevelSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = AcademicSublevelFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AcademicSublevelRepository()

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = AcademicSublevelService.soft_delete(pk, confirm=confirm)
        return ok_response(result)

    def get_queryset(self):
        return self.repository.get_all(active_only=False)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            obj = AcademicSublevelService.create_academic_sublevel(
                academic_level_id=data["academic_level"].id,
                code=data["code"],
                name=data["name"],
                description=data.get("description", ""),
            )
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))
        serializer.instance = obj

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        try:
            obj = AcademicSublevelService.update_academic_sublevel(
                serializer.instance.id, **data
            )
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))
        serializer.instance = obj
