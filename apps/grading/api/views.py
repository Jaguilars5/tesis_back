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
    ActivityType,
    BlockComponent,
    ComponentIndicator,
    EvaluationBlock,
    EvaluationType,
    EvaluativeActivity,
    GradeChangeHistory,
    GradeType,
    PeriodGradeSummary,
    ProjectNote,
    PromotionStatus,
    QualitativeScale,
    RecoveryProcess,
    RecoveryProcessType,
    StudentNote,
)
from ..repositories import (
    ActivityTypeRepository,
    BlockComponentRepository,
    ComponentIndicatorRepository,
    EvaluationBlockRepository,
    EvaluationTypeRepository,
    EvaluativeActivityRepository,
    GradeChangeHistoryRepository,
    GradeTypeRepository,
    PeriodGradeSummaryRepository,
    ProjectNoteRepository,
    PromotionStatusRepository,
    QualitativeScaleRepository,
    RecoveryProcessRepository,
    RecoveryProcessTypeRepository,
    StudentNoteRepository,
)
from .serializers import (
    ActivityTypeSerializer,
    BlockComponentSerializer,
    ComponentIndicatorSerializer,
    EvaluationBlockSerializer,
    EvaluationTypeSerializer,
    EvaluativeActivitySerializer,
    GradeChangeHistorySerializer,
    GradeTypeSerializer,
    PeriodGradeSummarySerializer,
    ProjectNoteSerializer,
    PromotionStatusSerializer,
    QualitativeScaleSerializer,
    RecoveryProcessSerializer,
    RecoveryProcessTypeSerializer,
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

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.repository.get_by_id(kwargs.get("pk"))
            if not instance:
                return Response(
                    f"{self.serializer_class.Meta.model.__name__} not found",
                    status=404,
                )
            if hasattr(instance, "is_active"):
                instance.is_active = False
                instance.save()
                return Response({"id": kwargs.get("pk"), "is_active": False})
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
        "list": grading.VIEW_EVALUATION_MACRO,
        "retrieve": grading.VIEW_EVALUATION_MACRO,
        "create": grading.CREATE_EVALUATION_MACRO,
        "update": grading.UPDATE_EVALUATION_MACRO,
        "partial_update": grading.UPDATE_EVALUATION_MACRO,
        "destroy": grading.DELETE_EVALUATION_MACRO,
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
)
class BlockComponentViewSet(BaseGradingViewSet):
    serializer_class = BlockComponentSerializer
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_EVALUATION_CRITERIA,
        "retrieve": grading.VIEW_EVALUATION_CRITERIA,
        "create": grading.CREATE_EVALUATION_CRITERIA,
        "update": grading.UPDATE_EVALUATION_CRITERIA,
        "partial_update": grading.UPDATE_EVALUATION_CRITERIA,
        "destroy": grading.DELETE_EVALUATION_CRITERIA,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = BlockComponentRepository()

    def get_queryset(self):
        return self.repository.get_all()


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
class ComponentIndicatorViewSet(BaseGradingViewSet):
    serializer_class = ComponentIndicatorSerializer
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_EVALUATION_SUBCRITERIA,
        "retrieve": grading.VIEW_EVALUATION_SUBCRITERIA,
        "create": grading.CREATE_EVALUATION_SUBCRITERIA,
        "update": grading.UPDATE_EVALUATION_SUBCRITERIA,
        "partial_update": grading.UPDATE_EVALUATION_SUBCRITERIA,
        "destroy": grading.DELETE_EVALUATION_SUBCRITERIA,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = ComponentIndicatorRepository()

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
    action_permissions = {
        "list": grading.VIEW_CLASS_ASSIGNMENT,
        "retrieve": grading.VIEW_CLASS_ASSIGNMENT,
        "create": grading.CREATE_CLASS_ASSIGNMENT,
        "update": grading.UPDATE_CLASS_ASSIGNMENT,
        "partial_update": grading.UPDATE_CLASS_ASSIGNMENT,
        "destroy": grading.DELETE_CLASS_ASSIGNMENT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = EvaluativeActivityRepository()

    def get_queryset(self):
        return self.repository.get_all()


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
    action_permissions = {
        "list": grading.VIEW_GRADE_SUMMARY,
        "retrieve": grading.VIEW_GRADE_SUMMARY,
        "create": grading.CREATE_GRADE_SUMMARY,
        "update": grading.UPDATE_GRADE_SUMMARY,
        "partial_update": grading.UPDATE_GRADE_SUMMARY,
        "destroy": grading.DELETE_GRADE_SUMMARY,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = PeriodGradeSummaryRepository()

    def get_queryset(self):
        return self.repository.get_all()


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
class RecoveryProcessViewSet(BaseGradingViewSet):
    serializer_class = RecoveryProcessSerializer
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_RECOVERY_PROCESS,
        "retrieve": grading.VIEW_RECOVERY_PROCESS,
        "create": grading.CREATE_RECOVERY_PROCESS,
        "update": grading.UPDATE_RECOVERY_PROCESS,
        "partial_update": grading.UPDATE_RECOVERY_PROCESS,
        "destroy": grading.DELETE_RECOVERY_PROCESS,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = RecoveryProcessRepository()

    def get_queryset(self):
        return self.repository.get_all()


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
class ProjectNoteViewSet(BaseGradingViewSet):
    serializer_class = ProjectNoteSerializer
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_PROJECT_NOTE,
        "retrieve": grading.VIEW_PROJECT_NOTE,
        "create": grading.CREATE_PROJECT_NOTE,
        "update": grading.UPDATE_PROJECT_NOTE,
        "partial_update": grading.UPDATE_PROJECT_NOTE,
        "destroy": grading.DELETE_PROJECT_NOTE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = ProjectNoteRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de calificación", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener tipo de calificación", tags=["grading"]),
)
class GradeTypeViewSet(BaseGradingViewSet):
    serializer_class = GradeTypeSerializer
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_GRADE_TYPE,
        "retrieve": grading.VIEW_GRADE_TYPE,
        "create": grading.CREATE_GRADE_TYPE,
        "update": grading.UPDATE_GRADE_TYPE,
        "partial_update": grading.UPDATE_GRADE_TYPE,
        "destroy": grading.DELETE_GRADE_TYPE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = GradeTypeRepository()

    def get_queryset(self):
        return self.repository.get_all()


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
    list=extend_schema(summary="Listar tipos de evaluación", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener tipo de evaluación", tags=["grading"]),
    create=extend_schema(summary="Crear tipo de evaluación", tags=["grading"]),
    update=extend_schema(summary="Actualizar tipo de evaluación", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar tipo de evaluación parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar tipo de evaluación", tags=["grading"]),
)
class EvaluationTypeViewSet(BaseGradingViewSet):
    serializer_class = EvaluationTypeSerializer
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_EVALUATION_TYPE,
        "retrieve": grading.VIEW_EVALUATION_TYPE,
        "create": grading.CREATE_EVALUATION_TYPE,
        "update": grading.UPDATE_EVALUATION_TYPE,
        "partial_update": grading.UPDATE_EVALUATION_TYPE,
        "destroy": grading.DELETE_EVALUATION_TYPE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = EvaluationTypeRepository()

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
    list=extend_schema(summary="Listar estados de promoción", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener estado de promoción", tags=["grading"]),
    create=extend_schema(summary="Crear estado de promoción", tags=["grading"]),
    update=extend_schema(summary="Actualizar estado de promoción", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar estado de promoción parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar estado de promoción", tags=["grading"]),
)
class PromotionStatusViewSet(BaseGradingViewSet):
    serializer_class = PromotionStatusSerializer
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_PROMOTION_STATUS,
        "retrieve": grading.VIEW_PROMOTION_STATUS,
        "create": grading.CREATE_PROMOTION_STATUS,
        "update": grading.UPDATE_PROMOTION_STATUS,
        "partial_update": grading.UPDATE_PROMOTION_STATUS,
        "destroy": grading.DELETE_PROMOTION_STATUS,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = PromotionStatusRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de proceso de recuperación", tags=["grading"]),
    retrieve=extend_schema(summary="Obtener tipo de proceso de recuperación", tags=["grading"]),
    create=extend_schema(summary="Crear tipo de proceso de recuperación", tags=["grading"]),
    update=extend_schema(summary="Actualizar tipo de proceso de recuperación", tags=["grading"]),
    partial_update=extend_schema(summary="Actualizar tipo de proceso de recuperación parcialmente", tags=["grading"]),
    destroy=extend_schema(summary="Eliminar tipo de proceso de recuperación", tags=["grading"]),
)
class RecoveryProcessTypeViewSet(viewsets.ModelViewSet):
    queryset = RecoveryProcessType.objects.all().order_by("name")
    serializer_class = RecoveryProcessTypeSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    pagination_class = StandardResultsSetPagination
    action_permissions = {
        "list": grading.VIEW_RECOVERY_PROCESS_TYPE,
        "retrieve": grading.VIEW_RECOVERY_PROCESS_TYPE,
        "create": grading.CREATE_RECOVERY_PROCESS_TYPE,
        "update": grading.UPDATE_RECOVERY_PROCESS_TYPE,
        "partial_update": grading.UPDATE_RECOVERY_PROCESS_TYPE,
        "destroy": grading.DELETE_RECOVERY_PROCESS_TYPE,
    }
