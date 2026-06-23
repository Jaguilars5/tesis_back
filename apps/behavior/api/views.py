from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.academic.models import AcademicPeriod
from apps.behavior.api.serializers import (
    BehaviorEvaluationSerializer,
    ConductIncidentSerializer,
    IncidentTypeSerializer,
    SeveritySerializer,
)
from apps.behavior.repositories import (
    BehaviorEvaluationRepository,
    ConductIncidentRepository,
    IncidentTypeRepository,
    SeverityRepository,
)
from apps.behavior.services.behavior_service import BehaviorEvaluationService
from apps.core.api.permissions import HasPermission
from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.api.scoping import scope_student_to_enrollment
from apps.core.constants.permissions import behavior
from apps.core.utils import ok_response
from apps.students.models import Enrollment


@extend_schema_view(
    list=extend_schema(summary="Listar incidentes", tags=["behavior"]),
    retrieve=extend_schema(summary="Obtener incidente", tags=["behavior"]),
    create=extend_schema(summary="Crear incidente", tags=["behavior"]),
    update=extend_schema(summary="Actualizar incidente", tags=["behavior"]),
    partial_update=extend_schema(summary="Actualizar incidente parcialmente", tags=["behavior"]),
    destroy=extend_schema(summary="Eliminar incidente", tags=["behavior"]),
)
class ConductIncidentViewSet(viewsets.ModelViewSet):
    serializer_class = ConductIncidentSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["enrollment"]
    action_permissions = {
        "list": behavior.VIEW_CONDUCT_INCIDENT,
        "retrieve": behavior.VIEW_CONDUCT_INCIDENT,
        "create": behavior.CREATE_CONDUCT_INCIDENT,
        "update": behavior.UPDATE_CONDUCT_INCIDENT,
        "partial_update": behavior.UPDATE_CONDUCT_INCIDENT,
        "destroy": behavior.DELETE_CONDUCT_INCIDENT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = ConductIncidentRepository()

    def get_queryset(self):
        qs = self.repository.get_all()
        return scope_student_to_enrollment(self.request, qs)


@extend_schema_view(
    list=extend_schema(summary="Listar evaluaciones conductuales", tags=["behavior"]),
    retrieve=extend_schema(summary="Obtener evaluación conductual", tags=["behavior"]),
    create=extend_schema(summary="Crear evaluación conductual", tags=["behavior"]),
    update=extend_schema(summary="Actualizar evaluación conductual", tags=["behavior"]),
    partial_update=extend_schema(summary="Actualizar evaluación parcialmente", tags=["behavior"]),
    destroy=extend_schema(summary="Eliminar evaluación conductual", tags=["behavior"]),
    related_incidents=extend_schema(summary="Incidentes relacionados", tags=["behavior"]),
)
class BehaviorEvaluationViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorEvaluationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["enrollment", "academic_period"]
    action_permissions = {
        "list": behavior.VIEW_BEHAVIOR_EVALUATION,
        "retrieve": behavior.VIEW_BEHAVIOR_EVALUATION,
        "create": behavior.CREATE_BEHAVIOR_EVALUATION,
        "update": behavior.UPDATE_BEHAVIOR_EVALUATION,
        "partial_update": behavior.UPDATE_BEHAVIOR_EVALUATION,
        "destroy": behavior.DELETE_BEHAVIOR_EVALUATION,
        "calculate": behavior.CREATE_BEHAVIOR_EVALUATION,
        "related_incidents": behavior.VIEW_BEHAVIOR_EVALUATION,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = BehaviorEvaluationRepository()

    def get_queryset(self):
        qs = self.repository.get_all()
        return scope_student_to_enrollment(self.request, qs)

    @extend_schema(
        summary="Calcular evaluación conductual",
        description="Ejecuta el cálculo automático de la escala conductual basado en los incidentes del estudiante en el período.",
        tags=["behavior"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "enrollment_id": {"type": "integer"},
                    "academic_period_id": {"type": "integer"},
                },
                "required": ["enrollment_id", "academic_period_id"],
            }
        },
    )
    @action(detail=False, methods=["post"])
    def calculate(self, request):
        enrollment_id = request.data.get("enrollment_id")
        academic_period_id = request.data.get("academic_period_id")
        enrollment = Enrollment.objects.get(pk=enrollment_id)
        academic_period = AcademicPeriod.objects.get(pk=academic_period_id)
        evaluation = BehaviorEvaluationService.calculate_behavior_evaluation(
            enrollment, academic_period
        )
        serializer = self.get_serializer(evaluation)
        return ok_response(serializer.data)

    @action(detail=True, methods=["get"])
    def related_incidents(self, request, pk=None):
        evaluation = self.get_object()
        incidents = ConductIncidentRepository.get_by_enrollment_and_period(
            enrollment_id=evaluation.enrollment_id,
            academic_period_id=evaluation.academic_period_id,
        )
        serializer = ConductIncidentSerializer(incidents, many=True)
        return ok_response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de incidente", tags=["behavior"]),
    retrieve=extend_schema(summary="Obtener tipo de incidente", tags=["behavior"]),
    create=extend_schema(summary="Crear tipo de incidente", tags=["behavior"]),
    update=extend_schema(summary="Actualizar tipo de incidente", tags=["behavior"]),
    partial_update=extend_schema(summary="Actualizar tipo de incidente parcialmente", tags=["behavior"]),
    destroy=extend_schema(summary="Eliminar tipo de incidente", tags=["behavior"]),
)
class IncidentTypeViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentTypeSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": behavior.VIEW_INCIDENT_TYPE,
        "retrieve": behavior.VIEW_INCIDENT_TYPE,
        "create": behavior.CREATE_INCIDENT_TYPE,
        "update": behavior.UPDATE_INCIDENT_TYPE,
        "partial_update": behavior.UPDATE_INCIDENT_TYPE,
        "destroy": behavior.DELETE_INCIDENT_TYPE,
        "soft_delete": behavior.DELETE_INCIDENT_TYPE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = IncidentTypeRepository()

    def get_queryset(self):
        return self.repository.get_all()

    @extend_schema(
        summary="Desactivar tipo de incidente",
        description="Realiza un soft delete del tipo de incidente (is_active = False).",
        tags=["behavior"],
    )
    @action(detail=True, methods=["post"])
    def soft_delete(self, request, pk=None):
        instance = self.get_object()
        result = self.repository.soft_delete(instance)
        return ok_response(result)


@extend_schema_view(
    list=extend_schema(summary="Listar severidades", tags=["behavior"]),
    retrieve=extend_schema(summary="Obtener severidad", tags=["behavior"]),
    create=extend_schema(summary="Crear severidad", tags=["behavior"]),
    update=extend_schema(summary="Actualizar severidad", tags=["behavior"]),
    partial_update=extend_schema(summary="Actualizar severidad parcialmente", tags=["behavior"]),
    destroy=extend_schema(summary="Eliminar severidad", tags=["behavior"]),
)
class SeverityViewSet(viewsets.ModelViewSet):
    serializer_class = SeveritySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": behavior.VIEW_SEVERITY,
        "retrieve": behavior.VIEW_SEVERITY,
        "create": behavior.CREATE_SEVERITY,
        "update": behavior.UPDATE_SEVERITY,
        "partial_update": behavior.UPDATE_SEVERITY,
        "destroy": behavior.DELETE_SEVERITY,
        "soft_delete": behavior.DELETE_SEVERITY,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SeverityRepository()

    def get_queryset(self):
        return self.repository.get_all()

    @extend_schema(
        summary="Desactivar severidad",
        description="Realiza un soft delete de la severidad (is_active = False).",
        tags=["behavior"],
    )
    @action(detail=True, methods=["post"])
    def soft_delete(self, request, pk=None):
        instance = self.get_object()
        result = self.repository.soft_delete(instance)
        return ok_response(result)