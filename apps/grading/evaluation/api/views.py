from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.grading.api.base import BaseGradingViewSet
from apps.core.utils import ok_response

from ..application.serializers import (
    EvaluationBlockSerializer,
    BlockComponentSerializer,
    EvaluativeActivitySerializer,
)
from ..infrastructure.repositories import (
    EvaluationBlockRepository,
    BlockComponentRepository,
    EvaluativeActivityRepository,
)
from ..permissions import ACTION_PERMISSIONS, BLOCK_COMPONENT_PERMISSIONS, EVALUATIVE_ACTIVITY_PERMISSIONS
from .filters import BlockComponentFilter, EvaluativeActivityFilter


@extend_schema_view(
    list=extend_schema(summary="Listar bloques de evaluaci\u00f3n", tags=["grading"]),
    get=extend_schema(summary="Obtener bloque de evaluaci\u00f3n", tags=["grading"]),
    create=extend_schema(summary="Crear bloque de evaluaci\u00f3n", tags=["grading"]),
    update=extend_schema(summary="Actualizar bloque de evaluaci\u00f3n", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar bloque parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar bloque de evaluaci\u00f3n", tags=["grading"]),
)
class EvaluationBlockViewSet(BaseGradingViewSet):
    serializer_class = EvaluationBlockSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "weight_percentage", "block_type"]
    ordering = ["academic_period", "subject_offering", "block_type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = EvaluationBlockRepository()

    def get_queryset(self):
        return self.repository.get_all()


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = BlockComponentRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar actividades evaluativas", tags=["grading"]),
    get=extend_schema(summary="Obtener actividad evaluativa", tags=["grading"]),
    create=extend_schema(summary="Crear actividad evaluativa", tags=["grading"]),
    update=extend_schema(summary="Actualizar actividad evaluativa", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar actividad parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar actividad evaluativa", tags=["grading"]),
)
class EvaluativeActivityViewSet(BaseGradingViewSet):
    serializer_class = EvaluativeActivitySerializer
    action_permissions = EVALUATIVE_ACTIVITY_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = EvaluativeActivityFilter
    search_fields = ["title"]
    ordering_fields = ["title", "due_date", "max_score"]
    ordering = ["-due_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = EvaluativeActivityRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        tss_id = data.get("teacher_subject_section")
        block_component_id = data.get("block_component")

        if not block_component_id or int(block_component_id) == 0:
            if not tss_id:
                return ok_response(
                    {"error": "teacher_subject_section es requerido"},
                    msg="Error",
                    status_code=400,
                )
            try:
                from apps.academic.teacher_subject_section.infrastructure.models import (
                    TeacherSubjectSection,
                )
                from ..infrastructure.models import BlockComponent

                tss = TeacherSubjectSection.objects.select_related(
                    "subject_offering"
                ).get(pk=tss_id)
                component = (
                    BlockComponent.objects.filter(
                        evaluation_block__subject_offering=tss.subject_offering,
                        is_active=True,
                    )
                    .select_related("evaluation_block")
                    .first()
                )
                if not component:
                    return ok_response(
                        {"error": "No existe un componente de bloque activo para esta clase. Configure los bloques de evaluaci\u00f3n primero."},
                        msg="Error",
                        status_code=400,
                    )
                data["block_component"] = component.id
            except TeacherSubjectSection.DoesNotExist:
                return ok_response(
                    {"error": "teacher_subject_section no encontrado"},
                    msg="Error",
                    status_code=400,
                )

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            instance = serializer.save()
            return ok_response(
                serializer.data,
                msg="Creado exitosamente",
                status_code=201,
            )
        return ok_response(serializer.errors, msg="Error de validaci\u00f3n", status_code=400)
