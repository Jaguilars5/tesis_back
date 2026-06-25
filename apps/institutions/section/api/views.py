from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter

from apps.core.utils import ok_response
from apps.institutions.api.base import BaseInstitutionsViewSet

from ..application.serializers import SectionSerializer
from ..domain.services import SectionService
from ..infrastructure.repositories import SectionRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import SectionFilter


@extend_schema_view(
    list=extend_schema(summary="Listar secciones", tags=["institutions"]),
    get=extend_schema(summary="Obtener secci\u00f3n", tags=["institutions"]),
    create=extend_schema(summary="Crear secci\u00f3n", tags=["institutions"]),
    update=extend_schema(summary="Actualizar secci\u00f3n", tags=["institutions"]),
    partial_update=extend_schema(summary="Actualizar secci\u00f3n parcialmente", tags=["institutions"]),
    destroy=extend_schema(summary="Eliminar secci\u00f3n", tags=["institutions"]),
    soft_delete=extend_schema(summary="Desactivar sección con cascada", tags=["institutions"]),
)
class SectionViewSet(BaseInstitutionsViewSet):
    serializer_class = SectionSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = SectionFilter
    ordering_fields = ["parallel", "capacity"]
    ordering = ["academic_grade__name", "parallel"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SectionRepository()

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = SectionService.soft_delete(pk, confirm=confirm)
        return ok_response(result)

    def get_queryset(self):
        search = self.request.query_params.get("search")
        return self.repository.get_all(search=search)

    def perform_create(self, serializer):
        data = serializer.validated_data
        obj = SectionService.create_section(**data)
        serializer.instance = obj

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        obj = SectionService.update_section(serializer.instance.id, **data)
        serializer.instance = obj
