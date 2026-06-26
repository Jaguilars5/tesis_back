from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.core.utils import ok_response
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
    soft_delete=extend_schema(summary="Desactivar tipo de actividad", tags=["grading"]),
)
class ActivityTypeViewSet(BaseGradingViewSet):
    serializer_class = ActivityTypeSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def get_queryset(self):
        return ActivityTypeRepository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            obj = ActivityTypeService.create_activity_type(
                code=data["code"],
                name=data["name"],
                description=data.get("description", ""),
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            obj = ActivityTypeService.update_activity_type(
                pk=serializer.instance.id,
                code=data.get("code"),
                name=data.get("name"),
                description=data.get("description", ""),
                is_active=data.get("is_active"),
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    @action(detail=True, methods=["post"])
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = ActivityTypeService.soft_delete(pk, confirm=confirm)
        return ok_response(result)
