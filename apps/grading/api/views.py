"""
Vistas de API para el módulo Grading.

Utiliza ViewSets de DRF para operaciones CRUD RESTful sobre calificaciones y evaluaciones.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.api.permissions import HasPermission
from apps.core.constants.permissions import grading

from ..models import (
    BlockComponent,
    ComponentIndicator,
    DiagnosticEvaluation,
    EvaluationBlock,
    EvaluativeActivity,
    GradeChangeHistory,
    GradeType,
    PeriodGradeSummary,
    ProjectNote,
    QualitativeScale,
    RecoveryProcess,
    StudentNote,
)
from ..repositories import StudentNoteRepository
from .serializers import (
    BlockComponentSerializer,
    ComponentIndicatorSerializer,
    DiagnosticEvaluationSerializer,
    EvaluationBlockSerializer,
    EvaluativeActivitySerializer,
    GradeChangeHistorySerializer,
    GradeTypeSerializer,
    PeriodGradeSummarySerializer,
    ProjectNoteSerializer,
    QualitativeScaleSerializer,
    RecoveryProcessSerializer,
    StudentNoteSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="Listar registros", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener registro", tags=["grading"]),
    create=extend_schema(summary="Crear registro", tags=["grading"]),
    update=extend_schema(summary="Actualizar registro", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar registro", tags=["grading"]),
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
                serializer.save()
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

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.repository.get_by_id(kwargs.get("pk"))
            if not instance:
                return Response(
                    f"{self.serializer_class.Meta.model.__name__} not found",
                    status=404,
                )
            if hasattr(instance, "active"):
                instance.active = False
                instance.save()
                return Response({"id": kwargs.get("pk"), "active": False})
            return Response(
                f"{self.serializer_class.Meta.model.__name__} does not support soft delete.",
                status=400,
            )
        except Exception as e:
            return Response(str(e), status=400)


class StudentNoteViewSet(BaseGradingViewSet):
    serializer_class = StudentNoteSerializer
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
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de calificación", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener tipo de calificación", tags=["grading"]),
)
class GradeTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GradeTypeSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": grading.VIEW_GRADE_TYPE,
        "retrieve": grading.VIEW_GRADE_TYPE,
    }

    def get_queryset(self):
        return GradeType.objects.all().order_by("name")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e), status=400)


@extend_schema_view(
    list=extend_schema(summary="Listar escalas cualitativas", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener escala cualitativa", tags=["grading"]),
)
class QualitativeScaleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QualitativeScaleSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": grading.VIEW_QUALITATIVE_SCALE,
        "retrieve": grading.VIEW_QUALITATIVE_SCALE,
    }

    def get_queryset(self):
        return QualitativeScale.objects.all().order_by("-numeric_equivalence")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e), status=400)


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
class EvaluationBlockViewSet(viewsets.ModelViewSet):
    serializer_class = EvaluationBlockSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_EVALUATION_MACRO,
        "retrieve": grading.VIEW_EVALUATION_MACRO,
        "create": grading.CREATE_EVALUATION_MACRO,
        "update": grading.UPDATE_EVALUATION_MACRO,
        "partial_update": grading.UPDATE_EVALUATION_MACRO,
        "destroy": grading.DELETE_EVALUATION_MACRO,
    }

    def get_queryset(self):
        return EvaluationBlock.objects.all().select_related("academic_period")


@extend_schema_view(
    list=extend_schema(summary="Listar componentes de bloque", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener componente de bloque", tags=["grading"]),
    create=extend_schema(summary="Crear componente de bloque", tags=["grading"]),
    update=extend_schema(summary="Actualizar componente de bloque", tags=["grading"]),
    partial_update=extend_schema(
        summary="Actualizar componente parcialmente", tags=["grading"]
    ),
    destroy=extend_schema(summary="Eliminar componente de bloque", tags=["grading"]),
)
class BlockComponentViewSet(viewsets.ModelViewSet):
    serializer_class = BlockComponentSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_EVALUATION_CRITERIA,
        "retrieve": grading.VIEW_EVALUATION_CRITERIA,
        "create": grading.CREATE_EVALUATION_CRITERIA,
        "update": grading.UPDATE_EVALUATION_CRITERIA,
        "partial_update": grading.UPDATE_EVALUATION_CRITERIA,
        "destroy": grading.DELETE_EVALUATION_CRITERIA,
    }

    def get_queryset(self):
        return BlockComponent.objects.all().select_related("evaluation_block")


@extend_schema_view(
    list=extend_schema(summary="Listar indicadores", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener indicador", tags=["grading"]),
    create=extend_schema(summary="Crear indicador", tags=["grading"]),
    update=extend_schema(summary="Actualizar indicador", tags=["grading"]),
    partial_update=extend_schema(
        summary="Actualizar indicador parcialmente", tags=["grading"]
    ),
    destroy=extend_schema(summary="Eliminar indicador", tags=["grading"]),
)
class ComponentIndicatorViewSet(viewsets.ModelViewSet):
    serializer_class = ComponentIndicatorSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_EVALUATION_SUBCRITERIA,
        "retrieve": grading.VIEW_EVALUATION_SUBCRITERIA,
        "create": grading.CREATE_EVALUATION_SUBCRITERIA,
        "update": grading.UPDATE_EVALUATION_SUBCRITERIA,
        "partial_update": grading.UPDATE_EVALUATION_SUBCRITERIA,
        "destroy": grading.DELETE_EVALUATION_SUBCRITERIA,
    }

    def get_queryset(self):
        return ComponentIndicator.objects.all().select_related("block_component")


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
class EvaluativeActivityViewSet(viewsets.ModelViewSet):
    serializer_class = EvaluativeActivitySerializer
    permission_classes = [IsAuthenticated, HasPermission]
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_CLASS_ASSIGNMENT,
        "retrieve": grading.VIEW_CLASS_ASSIGNMENT,
        "create": grading.CREATE_CLASS_ASSIGNMENT,
        "update": grading.UPDATE_CLASS_ASSIGNMENT,
        "partial_update": grading.UPDATE_CLASS_ASSIGNMENT,
        "destroy": grading.DELETE_CLASS_ASSIGNMENT,
    }

    def get_queryset(self):
        return EvaluativeActivity.objects.all().select_related(
            "component_indicator", "teacher_subject_section"
        )


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

    def get_queryset(self):
        return GradeChangeHistory.objects.all().select_related(
            "student_note", "modified_by_user"
        )


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
class PeriodGradeSummaryViewSet(viewsets.ModelViewSet):
    queryset = PeriodGradeSummary.objects.all().order_by("-id")
    serializer_class = PeriodGradeSummarySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": grading.VIEW_GRADE_SUMMARY,
        "retrieve": grading.VIEW_GRADE_SUMMARY,
        "create": grading.CREATE_GRADE_SUMMARY,
        "update": grading.UPDATE_GRADE_SUMMARY,
        "partial_update": grading.UPDATE_GRADE_SUMMARY,
        "destroy": grading.DELETE_GRADE_SUMMARY,
    }


@extend_schema_view(
    list=extend_schema(summary="Listar procesos de recuperación", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener proceso de recuperación", tags=["grading"]),
    create=extend_schema(summary="Crear proceso de recuperación", tags=["grading"]),
    update=extend_schema(
        summary="Actualizar proceso de recuperación", tags=["grading"]
    ),
    partial_update=extend_schema(
        summary="Actualizar proceso parcialmente", tags=["grading"]
    ),
    destroy=extend_schema(summary="Eliminar proceso de recuperación", tags=["grading"]),
)
class RecoveryProcessViewSet(viewsets.ModelViewSet):
    queryset = RecoveryProcess.objects.all()
    serializer_class = RecoveryProcessSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": grading.VIEW_RECOVERY_PROCESS,
        "retrieve": grading.VIEW_RECOVERY_PROCESS,
        "create": grading.CREATE_RECOVERY_PROCESS,
        "update": grading.UPDATE_RECOVERY_PROCESS,
        "partial_update": grading.UPDATE_RECOVERY_PROCESS,
        "destroy": grading.DELETE_RECOVERY_PROCESS,
    }


@extend_schema_view(
    list=extend_schema(summary="Listar evaluaciones diagnósticas", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener evaluación diagnóstica", tags=["grading"]),
    create=extend_schema(summary="Crear evaluación diagnóstica", tags=["grading"]),
    update=extend_schema(summary="Actualizar evaluación diagnóstica", tags=["grading"]),
    partial_update=extend_schema(
        summary="Actualizar evaluación parcialmente", tags=["grading"]
    ),
    destroy=extend_schema(summary="Eliminar evaluación diagnóstica", tags=["grading"]),
)
class DiagnosticEvaluationViewSet(viewsets.ModelViewSet):
    queryset = DiagnosticEvaluation.objects.all()
    serializer_class = DiagnosticEvaluationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": grading.VIEW_DIAGNOSTIC_EVALUATION,
        "retrieve": grading.VIEW_DIAGNOSTIC_EVALUATION,
        "create": grading.CREATE_DIAGNOSTIC_EVALUATION,
        "update": grading.UPDATE_DIAGNOSTIC_EVALUATION,
        "partial_update": grading.UPDATE_DIAGNOSTIC_EVALUATION,
        "destroy": grading.DELETE_DIAGNOSTIC_EVALUATION,
    }


@extend_schema_view(
    list=extend_schema(summary="Listar notas de proyecto", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener nota de proyecto", tags=["grading"]),
    create=extend_schema(summary="Crear nota de proyecto", tags=["grading"]),
    update=extend_schema(summary="Actualizar nota de proyecto", tags=["grading"]),
    partial_update=extend_schema(
        summary="Actualizar nota parcialmente", tags=["grading"]
    ),
    destroy=extend_schema(summary="Eliminar nota de proyecto", tags=["grading"]),
)
class ProjectNoteViewSet(viewsets.ModelViewSet):
    queryset = ProjectNote.objects.all().order_by("-id")
    serializer_class = ProjectNoteSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": grading.VIEW_PROJECT_NOTE,
        "retrieve": grading.VIEW_PROJECT_NOTE,
        "create": grading.CREATE_PROJECT_NOTE,
        "update": grading.UPDATE_PROJECT_NOTE,
        "partial_update": grading.UPDATE_PROJECT_NOTE,
        "destroy": grading.DELETE_PROJECT_NOTE,
    }
