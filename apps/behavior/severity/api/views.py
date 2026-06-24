from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.behavior.api.base import BaseBehaviorViewSet
from apps.core.utils import ok_response

from ..application.serializers import SeveritySerializer
from ..domain.services import SeverityService
from ..infrastructure.repositories import SeverityRepository
from ..permissions import ACTION_PERMISSIONS
from .filters import SeverityFilter


@extend_schema_view(
    list=extend_schema(summary="Listar severidades", tags=["behavior"]),
    get=extend_schema(summary="Obtener severidad", tags=["behavior"]),
    create=extend_schema(summary="Crear severidad", tags=["behavior"]),
    update=extend_schema(summary="Actualizar severidad", tags=["behavior"]),
    partial_update=extend_schema(summary="Actualizar parcialmente severidad", tags=["behavior"]),
    destroy=extend_schema(summary="Eliminar severidad", tags=["behavior"]),
    soft_delete=extend_schema(summary="Desactivar severidad", tags=["behavior"]),
)
class SeverityViewSet(BaseBehaviorViewSet):
    serializer_class = SeveritySerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = SeverityFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SeverityRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        obj = SeverityService.create_severity(
            code=data["code"],
            name=data["name"],
            description=data.get("description", ""),
        )
        serializer.instance = obj

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        obj = SeverityService.update_severity(serializer.instance.id, **data)
        serializer.instance = obj

    @action(detail=True, methods=["post"])
    def soft_delete(self, request, pk=None):
        instance = self.get_object()
        result = SeverityService.soft_delete_severity(instance.id)
        return ok_response(result)
