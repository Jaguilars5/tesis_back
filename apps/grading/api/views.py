"""
Vistas de API para el módulo Grading.

Utiliza ViewSets de DRF para operaciones CRUD RESTful sobre calificaciones,
asistencia e incidentes de conducta.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.pagination import StandardResultsSetPagination
from apps.core.permissions import HasPermission
from apps.core.constants.permissions import grading
from apps.core.utils import ok_response, error_response

from ..models import Attendance, AttendanceStatus, BehaviorEvaluation, ClassAssignment, ConductIncident, EvaluationCriteria, EvaluationMacro, EvaluationSubcriteria, GradeChangeHistory, GradeType, QualitativeScale, StudentNote
from ..repositories import (
    AttendanceRepository,
    ConductIncidentRepository,
    StudentNoteRepository,
)
from .serializers import (
    AttendanceSerializer,
    AttendanceStatusSerializer,
    BehaviorEvaluationSerializer,
    ClassAssignmentSerializer,
    ConductIncidentSerializer,
    EvaluationCriteriaSerializer,
    EvaluationMacroSerializer,
    EvaluationSubcriteriaSerializer,
    GradeChangeHistorySerializer,
    GradeTypeSerializer,
    QualitativeScaleSerializer,
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
                return error_response(
                    f"{self.serializer_class.Meta.model.__name__} not found",
                    404,
                )
            serializer = self.get_serializer(instance)
            return ok_response(serializer.data)
        except Exception as e:
            return error_response(e)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ok_response(serializer.data, status=201)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(e)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.repository.get_by_id(kwargs.get("pk"))
            if not instance:
                return error_response(
                    f"{self.serializer_class.Meta.model.__name__} not found",
                    404,
                )
            partial = kwargs.pop("partial", False)
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            if serializer.is_valid():
                serializer.save()
                return ok_response(serializer.data)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(e)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.repository.get_by_id(kwargs.get("pk"))
            if not instance:
                return error_response(
                    f"{self.serializer_class.Meta.model.__name__} not found",
                    404,
                )
            if hasattr(instance, "active"):
                instance.active = False
                instance.save()
                return ok_response({"id": kwargs.get("pk"), "active": False})
            return error_response(
                f"{self.serializer_class.Meta.model.__name__} does not support soft delete."
            )
        except Exception as e:
            return error_response(e)


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


class AttendanceViewSet(BaseGradingViewSet):
    serializer_class = AttendanceSerializer
    action_permissions = {
        "list": grading.VIEW_ATTENDANCE,
        "retrieve": grading.VIEW_ATTENDANCE,
        "create": grading.CREATE_ATTENDANCE,
        "update": grading.UPDATE_ATTENDANCE,
        "partial_update": grading.UPDATE_ATTENDANCE,
        "destroy": grading.DELETE_ATTENDANCE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AttendanceRepository()

    def get_queryset(self):
        return self.repository.get_all()


class ConductIncidentViewSet(BaseGradingViewSet):
    serializer_class = ConductIncidentSerializer
    action_permissions = {
        "list": grading.VIEW_INCIDENT,
        "retrieve": grading.VIEW_INCIDENT,
        "create": grading.CREATE_INCIDENT,
        "update": grading.UPDATE_INCIDENT,
        "partial_update": grading.UPDATE_INCIDENT,
        "destroy": grading.DELETE_INCIDENT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = ConductIncidentRepository()

    def get_queryset(self):
        return self.repository.get_all()


class AttendanceStatusViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttendanceStatusSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": grading.VIEW_ATTENDANCE_STATUS,
        "retrieve": grading.VIEW_ATTENDANCE_STATUS,
    }

    def get_queryset(self):
        return AttendanceStatus.objects.all().order_by("name")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ok_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return ok_response(serializer.data)
        except Exception as e:
            return error_response(e)


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
        return ok_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return ok_response(serializer.data)
        except Exception as e:
            return error_response(e)


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
        return ok_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return ok_response(serializer.data)
        except Exception as e:
            return error_response(e)


class BehaviorEvaluationViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorEvaluationSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": grading.VIEW_BEHAVIOR_EVALUATION,
        "retrieve": grading.VIEW_BEHAVIOR_EVALUATION,
        "create": grading.CREATE_BEHAVIOR_EVALUATION,
        "update": grading.UPDATE_BEHAVIOR_EVALUATION,
        "partial_update": grading.UPDATE_BEHAVIOR_EVALUATION,
        "destroy": grading.DELETE_BEHAVIOR_EVALUATION,
    }

    def get_queryset(self):
        return BehaviorEvaluation.objects.all().select_related(
            "enrollment__student__person", "academic_period", "calculated_scale", "final_scale"
        )


class EvaluationMacroViewSet(viewsets.ModelViewSet):
    serializer_class = EvaluationMacroSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": grading.VIEW_EVALUATION_MACRO,
        "retrieve": grading.VIEW_EVALUATION_MACRO,
        "create": grading.CREATE_EVALUATION_MACRO,
        "update": grading.UPDATE_EVALUATION_MACRO,
        "partial_update": grading.UPDATE_EVALUATION_MACRO,
        "destroy": grading.DELETE_EVALUATION_MACRO,
    }

    def get_queryset(self):
        return EvaluationMacro.objects.all().select_related("academic_period")


class EvaluationCriteriaViewSet(viewsets.ModelViewSet):
    serializer_class = EvaluationCriteriaSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": grading.VIEW_EVALUATION_CRITERIA,
        "retrieve": grading.VIEW_EVALUATION_CRITERIA,
        "create": grading.CREATE_EVALUATION_CRITERIA,
        "update": grading.UPDATE_EVALUATION_CRITERIA,
        "partial_update": grading.UPDATE_EVALUATION_CRITERIA,
        "destroy": grading.DELETE_EVALUATION_CRITERIA,
    }

    def get_queryset(self):
        return EvaluationCriteria.objects.all().select_related("evaluation_macro")


class EvaluationSubcriteriaViewSet(viewsets.ModelViewSet):
    serializer_class = EvaluationSubcriteriaSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": grading.VIEW_EVALUATION_SUBCRITERIA,
        "retrieve": grading.VIEW_EVALUATION_SUBCRITERIA,
        "create": grading.CREATE_EVALUATION_SUBCRITERIA,
        "update": grading.UPDATE_EVALUATION_SUBCRITERIA,
        "partial_update": grading.UPDATE_EVALUATION_SUBCRITERIA,
        "destroy": grading.DELETE_EVALUATION_SUBCRITERIA,
    }

    def get_queryset(self):
        return EvaluationSubcriteria.objects.all().select_related("evaluation_criteria")


class ClassAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = ClassAssignmentSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": grading.VIEW_CLASS_ASSIGNMENT,
        "retrieve": grading.VIEW_CLASS_ASSIGNMENT,
        "create": grading.CREATE_CLASS_ASSIGNMENT,
        "update": grading.UPDATE_CLASS_ASSIGNMENT,
        "partial_update": grading.UPDATE_CLASS_ASSIGNMENT,
        "destroy": grading.DELETE_CLASS_ASSIGNMENT,
    }

    def get_queryset(self):
        return ClassAssignment.objects.all().select_related(
            "evaluation_subcriteria", "teacher_subject_section"
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
