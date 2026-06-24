from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.grading.api.base import BaseGradingViewSet

from ..application.serializers import ActivityTypeSerializer
from ..domain.services import ActivityTypeService
from ..infrastructure.repositories import ActivityTypeRepository
from ..permissions import ACTION_PERMISSIONS


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de actividad", tags=["grading"]),
    get=extend_schema(summary="Obtener tipo de actividad", tags=["grading"]),
    create=extend_schema(summary="Crear tipo de actividad", tags=["grading"]),
    update=extend_schema(summary="Actualizar tipo de actividad", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar parcialmente tipo de actividad", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar tipo de actividad", tags=["grading"]),
)
class ActivityTypeViewSet(BaseGradingViewSet):
    serializer_class = ActivityTypeSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = ActivityTypeRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        obj = ActivityTypeService.create_activity_type(
            code=data["code"],
            name=data["name"],
            description=data.get("description", ""),
        )
        serializer.instance = obj

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        obj = ActivityTypeService.update_activity_type(serializer.instance.id, **data)
        serializer.instance = obj
