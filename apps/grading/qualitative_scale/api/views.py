from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.core.utils import ok_response
from apps.grading.api.base import BaseGradingViewSet

from ..application.serializers import (
    QualitativeScaleSerializer,
    QualitativeScaleSublevelSerializer,
)
from ..domain.services import QualitativeScaleService
from ..infrastructure.repositories import (
    QualitativeScaleRepository,
    QualitativeScaleSublevelRepository,
)
from ..permissions import ACTION_PERMISSIONS
from .filters import QualitativeScaleFilter, QualitativeScaleSublevelFilter


@extend_schema_view(
    list=extend_schema(summary="Listar escalas cualitativas", tags=["grading"]),
    get=extend_schema(summary="Obtener escala cualitativa", tags=["grading"]),
    create=extend_schema(summary="Crear escala cualitativa", tags=["grading"]),
    update=extend_schema(summary="Actualizar escala cualitativa", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar parcialmente escala cualitativa", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar escala cualitativa", tags=["grading"]),
    soft_delete=extend_schema(summary="Desactivar escala cualitativa", tags=["grading"]),
)
class QualitativeScaleViewSet(BaseGradingViewSet):
    serializer_class = QualitativeScaleSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = QualitativeScaleFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code", "numeric_equivalence"]
    ordering = ["-numeric_equivalence"]

    def get_queryset(self):
        return QualitativeScaleRepository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            obj = QualitativeScaleService.create_qualitative_scale(
                code=data["code"],
                name=data.get("name", ""),
                description=data["description"],
                numeric_equivalence=data["numeric_equivalence"],
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            obj = QualitativeScaleService.update_qualitative_scale(
                pk=serializer.instance.id,
                code=data.get("code"),
                name=data.get("name", ""),
                description=data.get("description"),
                numeric_equivalence=data.get("numeric_equivalence"),
                is_active=data.get("is_active"),
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    @action(detail=True, methods=["post"])
    def soft_delete(self, request, pk=None, url_path="soft-delete"):
        confirm = request.data.get("confirm", False)
        result = QualitativeScaleService.soft_delete(pk, confirm=confirm)
        return ok_response(result)


@extend_schema_view(
    list=extend_schema(summary="Listar escalas por subnivel", tags=["grading"]),
    get=extend_schema(summary="Obtener escala por subnivel", tags=["grading"]),
    create=extend_schema(summary="Asignar escala a subnivel", tags=["grading"]),
    update=extend_schema(summary="Actualizar asignacion escala-subnivel", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar asignacion parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar asignacion escala-subnivel", tags=["grading"]),
)
class QualitativeScaleSublevelViewSet(BaseGradingViewSet):
    serializer_class = QualitativeScaleSublevelSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = QualitativeScaleSublevelFilter

    def get_queryset(self):
        return QualitativeScaleSublevelRepository.get_all()
