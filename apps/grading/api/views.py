"""
Vistas de API para el módulo Grading.

Utiliza ViewSets de DRF para operaciones CRUD RESTful sobre calificaciones y evaluaciones.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.utils import ok_response, error_response
from .filters import BlockComponentFilter, EvaluativeActivityFilter

from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.api.permissions import HasPermission
from apps.core.api.scoping import scope_student_to_enrollment
from apps.core.constants.permissions import grading

from ..models import (
    ActivityType,
    BlockComponent,
    EvaluationBlock,
    EvaluativeActivity,
    GradeChangeHistory,
    PeriodGradeSummary,
    QualitativeScale,
    QualitativeScaleSublevel,
    StudentNote,
)
from ..repositories import (
    ActivityTypeRepository,
    BlockComponentRepository,
    EvaluationBlockRepository,
    EvaluativeActivityRepository,
    GradeChangeHistoryRepository,
    PeriodGradeSummaryRepository,
    QualitativeScaleRepository,
    QualitativeScaleSublevelRepository,
    StudentNoteRepository,
)
from .serializers import (
    ActivityTypeSerializer,
    BlockComponentSerializer,
    EvaluationBlockSerializer,
    EvaluativeActivitySerializer,
    GradeChangeHistorySerializer,
    PeriodGradeSummarySerializer,
    QualitativeScaleSerializer,
    QualitativeScaleSublevelSerializer,
    StudentNoteSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="Listar registros", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener registro", tags=["grading"]),
    create=extend_schema(summary="Crear registro", tags=["grading"]),
    update=extend_schema(summary="Actualizar registro", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar registro", tags=["grading"]),
    soft_delete=extend_schema(
        summary="Desactivar registro (soft delete)", tags=["grading"],
    ),
)
class BaseGradingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasPermission]
    pagination_class = StandardResultsSetPagination

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.repository.get_by_id(kwargs.get("pk"))
            if not instance:
                return Response(
                    f"{self.serializer_class.Meta.model.__name__} not found",
                    status=404,
                )
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e), status=400)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                if hasattr(instance, "full_clean"):
                    instance.full_clean()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            return Response(str(e), status=400)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.repository.get_by_id(kwargs.get("pk"))
            if not instance:
                return Response(
                    f"{self.serializer_class.Meta.model.__name__} not found",
                    status=404,
                )
            partial = kwargs.pop("partial", False)
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Exception as e:
            return Response(str(e), status=400)

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        instance = self.get_object()
        if hasattr(instance, "is_active"):
            instance.is_active = False
            instance.save()
            return ok_response({"id": instance.id, "is_active": False})
        return error_response("Este modelo no soporta borrado lógico")


class StudentNoteViewSet(BaseGradingViewSet):
    serializer_class = StudentNoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["enrollment", "evaluative_activity"]
    action_permissions = {
        "list": grading.VIEW_NOTE,
        "retrieve": grading.VIEW_NOTE,
        "create": grading.CREATE_NOTE,
        "update": grading.UPDATE_NOTE,
        "partial_update": grading.UPDATE_NOTE,
        "destroy": grading.DELETE_NOTE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = StudentNoteRepository()

    def get_queryset(self):
        qs = self.repository.get_all()
        return scope_student_to_enrollment(self.request, qs)


@extend_schema_view(
    list=extend_schema(summary="Listar bloques de evaluación", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener bloque de evaluación", tags=["grading"]),
    create=extend_schema(summary="Crear bloque de evaluación", tags=["grading"]),
    update=extend_schema(summary="Actualizar bloque de evaluación", tags=["grading"]),
    partial_update=extend_schema(
        summary="Actualizar bloque parcialmente", tags=["grading"]
    ),
    destroy=extend_schema(summary="Eliminar bloque de evaluación", tags=["grading"]),
)
class EvaluationBlockViewSet(BaseGradingViewSet):
    serializer_class = EvaluationBlockSerializer
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_EVALUATION_BLOCK,
        "retrieve": grading.VIEW_EVALUATION_BLOCK,
        "create": grading.CREATE_EVALUATION_BLOCK,
        "update": grading.UPDATE_EVALUATION_BLOCK,
        "partial_update": grading.UPDATE_EVALUATION_BLOCK,
        "destroy": grading.DELETE_EVALUATION_BLOCK,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = EvaluationBlockRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar componentes de bloque", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener componente de bloque", tags=["grading"]),
    create=extend_schema(summary="Crear componente de bloque", tags=["grading"]),
    update=extend_schema(summary="Actualizar componente de bloque", tags=["grading"]),
    partial_update=extend_schema(
        summary="Actualizar componente parcialmente", tags=["grading"]
    ),
    destroy=extend_schema(summary="Eliminar componente de bloque", tags=["grading"]),
    soft_delete=extend_schema(
        summary="Desactivar componente de bloque (soft delete)",
        tags=["grading"],
    ),
)
class BlockComponentViewSet(BaseGradingViewSet):
    serializer_class = BlockComponentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = BlockComponentFilter
    action_permissions = {
        "list": grading.VIEW_BLOCK_COMPONENT,
        "retrieve": grading.VIEW_BLOCK_COMPONENT,
        "create": grading.CREATE_BLOCK_COMPONENT,
        "update": grading.UPDATE_BLOCK_COMPONENT,
        "partial_update": grading.UPDATE_BLOCK_COMPONENT,
        "destroy": grading.DELETE_BLOCK_COMPONENT,
        "soft_delete": grading.DELETE_BLOCK_COMPONENT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = BlockComponentRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar actividades evaluativas", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener actividad evaluativa", tags=["grading"]),
    create=extend_schema(summary="Crear actividad evaluativa", tags=["grading"]),
    update=extend_schema(summary="Actualizar actividad evaluativa", tags=["grading"]),
    partial_update=extend_schema(
        summary="Actualizar actividad parcialmente", tags=["grading"]
    ),
    destroy=extend_schema(summary="Eliminar actividad evaluativa", tags=["grading"]),
)
class EvaluativeActivityViewSet(BaseGradingViewSet):
    serializer_class = EvaluativeActivitySerializer
    pagination_class = StandardResultsSetPagination
    ordering_fields = ["id", "title", "due_date", "created_at", "updated_at"]
    ordering = ["-due_date"]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EvaluativeActivityFilter
    action_permissions = {
        "list": grading.VIEW_EVALUATIVE_ACTIVITY,
        "retrieve": grading.VIEW_EVALUATIVE_ACTIVITY,
        "create": grading.CREATE_EVALUATIVE_ACTIVITY,
        "update": grading.UPDATE_EVALUATIVE_ACTIVITY,
        "partial_update": grading.UPDATE_EVALUATIVE_ACTIVITY,
        "destroy": grading.DELETE_EVALUATIVE_ACTIVITY,
        "soft_delete": grading.DELETE_EVALUATIVE_ACTIVITY,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = EvaluativeActivityRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def create(self, request, *args, **kwargs):
        """
        Si el cliente no envía un block_component válido (o envía 0),
        se auto-resuelve buscando el primer BlockComponent activo cuyo
        EvaluationBlock esté ligado al SubjectOffering del TSS enviado.
        """
        data = request.data.copy()
        tss_id = data.get("teacher_subject_section")
        block_component_id = data.get("block_component")

        # Resolver automáticamente si no se provee un ID válido
        if not block_component_id or int(block_component_id) == 0:
            if not tss_id:
                return error_response(
                    "teacher_subject_section es requerido",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            try:
                from apps.academic.models import TeacherSubjectSection
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
                    return error_response(
                        "No existe un componente de bloque activo para esta clase. "
                        "Configure los bloques de evaluación primero.",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
                data["block_component"] = component.id
            except TeacherSubjectSection.DoesNotExist:
                return error_response(
                    "teacher_subject_section no encontrado",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(summary="Listar historial de cambios", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener cambio de nota", tags=["grading"]),
)
class GradeChangeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GradeChangeHistorySerializer
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": grading.VIEW_GRADE_HISTORY,
        "retrieve": grading.VIEW_GRADE_HISTORY,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = GradeChangeHistoryRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar resúmenes de notas", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener resumen de notas", tags=["grading"]),
    create=extend_schema(summary="Crear resumen de notas", tags=["grading"]),
    update=extend_schema(summary="Actualizar resumen de notas", tags=["grading"]),
    partial_update=extend_schema(
        summary="Actualizar resumen parcialmente", tags=["grading"]
    ),
    destroy=extend_schema(summary="Eliminar resumen de notas", tags=["grading"]),
)
class PeriodGradeSummaryViewSet(BaseGradingViewSet):
    serializer_class = PeriodGradeSummarySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["enrollment", "academic_period"]
    action_permissions = {
        "list": grading.VIEW_GRADE_SUMMARY,
        "retrieve": grading.VIEW_GRADE_SUMMARY,
        "create": grading.CREATE_GRADE_SUMMARY,
        "update": grading.UPDATE_GRADE_SUMMARY,
        "partial_update": grading.UPDATE_GRADE_SUMMARY,
        "destroy": grading.DELETE_GRADE_SUMMARY,
        "recalculate": grading.RECALCULATE_GRADE_SUMMARY,
        "recalculate_period": grading.RECALCULATE_GRADE_SUMMARY,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = PeriodGradeSummaryRepository()

    def get_queryset(self):
        qs = self.repository.get_all()
        return scope_student_to_enrollment(self.request, qs)

    @extend_schema(
        summary="Recalcular un resumen de notas (enrollment, offering, period)",
        tags=["grading"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "enrollment_id": {"type": "integer"},
                    "subject_offering_id": {"type": "integer"},
                    "academic_period_id": {"type": "integer"},
                },
                "required": ["enrollment_id", "subject_offering_id", "academic_period_id"],
            }
        },
        responses={202: {"type": "object"}},
    )
    @action(detail=False, methods=["post"], url_path="recalculate")
    def recalculate(self, request):
        from apps.grading.tasks import recompute_period_grade_summary_task

        try:
            enrollment_id = int(request.data.get("enrollment_id"))
            offering_id = int(request.data.get("subject_offering_id"))
            period_id = int(request.data.get("academic_period_id"))
        except (TypeError, ValueError):
            return Response(
                "enrollment_id, subject_offering_id y academic_period_id son requeridos",
                status=400,
            )

        task = recompute_period_grade_summary_task.delay(
            enrollment_id, offering_id, period_id
        )
        return Response({"task_id": task.id, "status": "PENDING"}, status=202)

    @extend_schema(
        summary="Recalcular todos los resúmenes de un período académico",
        tags=["grading"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "academic_period_id": {"type": "integer"},
                },
                "required": ["academic_period_id"],
            }
        },
        responses={202: {"type": "object"}},
    )
    @action(detail=False, methods=["post"], url_path="recalculate-period")
    def recalculate_period(self, request):
        from apps.academic.repositories.academic_repo import AcademicPeriodRepository
        from apps.grading.services.grade_calculation_service import (
            GradeCalculationService,
        )

        try:
            period_id = int(request.data.get("academic_period_id"))
        except (TypeError, ValueError):
            return Response("academic_period_id es requerido", status=400)

        if not AcademicPeriodRepository.get_by_id(period_id):
            return Response("academic_period_id no existe", status=404)

        ids = GradeCalculationService.calculate_all_for_period(period_id)
        return Response(
            {"status": "OK", "summaries_calculated": len(ids), "ids": ids},
            status=202,
        )


@extend_schema_view(
    list=extend_schema(summary="Listar escalas cualitativas", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener escala cualitativa", tags=["grading"]),
)
class QualitativeScaleViewSet(BaseGradingViewSet):
    serializer_class = QualitativeScaleSerializer
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_QUALITATIVE_SCALE,
        "retrieve": grading.VIEW_QUALITATIVE_SCALE,
        "create": grading.CREATE_QUALITATIVE_SCALE,
        "update": grading.UPDATE_QUALITATIVE_SCALE,
        "partial_update": grading.UPDATE_QUALITATIVE_SCALE,
        "destroy": grading.DELETE_QUALITATIVE_SCALE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = QualitativeScaleRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de actividad", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener tipo de actividad", tags=["grading"]),
    create=extend_schema(summary="Crear tipo de actividad", tags=["grading"]),
    update=extend_schema(summary="Actualizar tipo de actividad", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar tipo de actividad parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar tipo de actividad", tags=["grading"]),
)
class ActivityTypeViewSet(BaseGradingViewSet):
    serializer_class = ActivityTypeSerializer
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_ACTIVITY_TYPE,
        "retrieve": grading.VIEW_ACTIVITY_TYPE,
        "create": grading.CREATE_ACTIVITY_TYPE,
        "update": grading.UPDATE_ACTIVITY_TYPE,
        "partial_update": grading.UPDATE_ACTIVITY_TYPE,
        "destroy": grading.DELETE_ACTIVITY_TYPE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = ActivityTypeRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar escalas por subnivel", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener escala por subnivel", tags=["grading"]),
    create=extend_schema(summary="Asignar escala a subnivel", tags=["grading"]),
    update=extend_schema(summary="Actualizar asignación escala-subnivel", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar asignación parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar asignación escala-subnivel", tags=["grading"]),
)
class QualitativeScaleSublevelViewSet(BaseGradingViewSet):
    serializer_class = QualitativeScaleSublevelSerializer
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_QUALITATIVE_SCALE,
        "retrieve": grading.VIEW_QUALITATIVE_SCALE,
        "create": grading.CREATE_QUALITATIVE_SCALE,
        "update": grading.UPDATE_QUALITATIVE_SCALE,
        "partial_update": grading.UPDATE_QUALITATIVE_SCALE,
        "destroy": grading.DELETE_QUALITATIVE_SCALE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = QualitativeScaleSublevelRepository()

    def get_queryset(self):
        return self.repository.get_all()
