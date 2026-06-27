from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.core.utils import ok_response, error_response
from apps.grading.api.base import BaseGradingViewSet

from ..application.serializers import (
    EvaluationBlockSerializer,
    BlockComponentSerializer,
    EvaluativeActivitySerializer,
)
from ..domain.services import EvaluationService
from ..infrastructure.repositories import (
    EvaluationBlockRepository,
    BlockComponentRepository,
    EvaluativeActivityRepository,
)
from ..permissions import ACTION_PERMISSIONS, BLOCK_COMPONENT_PERMISSIONS, EVALUATIVE_ACTIVITY_PERMISSIONS
from .filters import EvaluationBlockFilter, BlockComponentFilter, EvaluativeActivityFilter


@extend_schema_view(
    list=extend_schema(summary="Listar bloques de evaluacion", tags=["grading"]),
    get=extend_schema(summary="Obtener bloque de evaluacion", tags=["grading"]),
    create=extend_schema(summary="Crear bloque de evaluacion", tags=["grading"]),
    update=extend_schema(summary="Actualizar bloque de evaluacion", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar bloque parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar bloque de evaluacion", tags=["grading"]),
    soft_delete=extend_schema(summary="Desactivar bloque de evaluacion", tags=["grading"]),
)
class EvaluationBlockViewSet(BaseGradingViewSet):
    serializer_class = EvaluationBlockSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = EvaluationBlockFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "weight_percentage", "block_type"]
    ordering = ["academic_period", "subject_offering", "block_type"]

    def get_queryset(self):
        return EvaluationBlockRepository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            obj = EvaluationBlockRepository.create(**data)
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            obj = EvaluationBlockRepository.update(serializer.instance.id, **data)
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = EvaluationService.soft_delete_block(pk, confirm=confirm)
        return ok_response(result)


@extend_schema_view(
    list=extend_schema(summary="Listar componentes de bloque", tags=["grading"]),
    get=extend_schema(summary="Obtener componente de bloque", tags=["grading"]),
    create=extend_schema(summary="Crear componente de bloque", tags=["grading"]),
    update=extend_schema(summary="Actualizar componente de bloque", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar componente parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar componente de bloque", tags=["grading"]),
    soft_delete=extend_schema(summary="Desactivar componente de bloque", tags=["grading"]),
)
class BlockComponentViewSet(BaseGradingViewSet):
    serializer_class = BlockComponentSerializer
    action_permissions = BLOCK_COMPONENT_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = BlockComponentFilter
    search_fields = ["name"]
    ordering_fields = ["name", "internal_weight"]
    ordering = ["evaluation_block", "name"]

    def get_queryset(self):
        return BlockComponentRepository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            obj = BlockComponentRepository.create(**data)
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            obj = BlockComponentRepository.update(serializer.instance.id, **data)
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = EvaluationService.soft_delete_component(pk, confirm=confirm)
        return ok_response(result)


@extend_schema_view(
    list=extend_schema(summary="Listar actividades evaluativas", tags=["grading"]),
    get=extend_schema(summary="Obtener actividad evaluativa", tags=["grading"]),
    create=extend_schema(summary="Crear actividad evaluativa", tags=["grading"]),
    update=extend_schema(summary="Actualizar actividad evaluativa", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar actividad parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar actividad evaluativa", tags=["grading"]),
    soft_delete=extend_schema(summary="Desactivar actividad evaluativa", tags=["grading"]),
)
class EvaluativeActivityViewSet(BaseGradingViewSet):
    serializer_class = EvaluativeActivitySerializer
    action_permissions = EVALUATIVE_ACTIVITY_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = EvaluativeActivityFilter
    search_fields = ["title"]
    ordering_fields = ["title", "due_date", "max_score"]
    ordering = ["-due_date"]

    def get_queryset(self):
        return EvaluativeActivityRepository.get_all()

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            obj = EvaluationService.create_evaluative_activity(
                block_component_id=data.get("block_component").id if data.get("block_component") else None,
                teacher_subject_section_id=data.get("teacher_subject_section").id if data.get("teacher_subject_section") else None,
                title=data.get("title"),
                max_score=data.get("max_score"),
                due_date=data.get("due_date"),
                internal_weight=data.get("internal_weight", 100),
                activity_type_id=data.get("activity_type").id if data.get("activity_type") else None,
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            obj = EvaluativeActivityRepository.update(
                serializer.instance.id,
                title=data.get("title"),
                max_score=data.get("max_score"),
                due_date=data.get("due_date"),
                internal_weight=data.get("internal_weight"),
                activity_type_id=data.get("activity_type").id if data.get("activity_type") else None,
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    @action(detail=True, methods=["post"], url_path="soft-delete"   )
    def soft_delete(self, request, pk=None):
        confirm = request.data.get("confirm", False)
        result = EvaluationService.soft_delete_activity(pk, confirm=confirm)
        return ok_response(result)
