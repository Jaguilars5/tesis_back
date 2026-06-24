from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import SearchFilter, OrderingFilter

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


@extend_schema_view(
    list=extend_schema(summary="Listar escalas cualitativas", tags=["grading"]),
    get=extend_schema(summary="Obtener escala cualitativa", tags=["grading"]),
    create=extend_schema(summary="Crear escala cualitativa", tags=["grading"]),
    update=extend_schema(summary="Actualizar escala cualitativa", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar parcialmente escala cualitativa", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar escala cualitativa", tags=["grading"]),
)
class QualitativeScaleViewSet(BaseGradingViewSet):
    serializer_class = QualitativeScaleSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code", "numeric_equivalence"]
    ordering = ["-numeric_equivalence"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = QualitativeScaleRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        obj = QualitativeScaleService.create_qualitative_scale(
            code=data["code"],
            name=data.get("name", ""),
            description=data["description"],
            numeric_equivalence=data["numeric_equivalence"],
        )
        serializer.instance = obj

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        obj = QualitativeScaleService.update_qualitative_scale(serializer.instance.id, **data)
        serializer.instance = obj


@extend_schema_view(
    list=extend_schema(summary="Listar escalas por subnivel", tags=["grading"]),
    get=extend_schema(summary="Obtener escala por subnivel", tags=["grading"]),
    create=extend_schema(summary="Asignar escala a subnivel", tags=["grading"]),
    update=extend_schema(summary="Actualizar asignaci\u00f3n escala-subnivel", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar asignaci\u00f3n parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar asignaci\u00f3n escala-subnivel", tags=["grading"]),
)
class QualitativeScaleSublevelViewSet(BaseGradingViewSet):
    serializer_class = QualitativeScaleSublevelSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = QualitativeScaleSublevelRepository()

    def get_queryset(self):
        return self.repository.get_all()
