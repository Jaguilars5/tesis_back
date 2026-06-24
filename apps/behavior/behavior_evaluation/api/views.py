from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.academic.academic_period.infrastructure.models import AcademicPeriod
from apps.behavior.api.base import BaseBehaviorViewSet
from apps.behavior.conduct_incident.application.serializers import (
    ConductIncidentSerializer,
)
from apps.behavior.conduct_incident.infrastructure.repositories import (
    ConductIncidentRepository,
)
from apps.core.api.scoping import scope_student_to_enrollment
from apps.core.utils import ok_response
from apps.students.models import Enrollment

from ..application.serializers import BehaviorEvaluationSerializer
from ..domain.services import BehaviorEvaluationService
from ..infrastructure.repositories import BehaviorEvaluationRepository
from ..permissions import ACTION_PERMISSIONS


@extend_schema_view(
    list=extend_schema(summary="Listar evaluaciones conductuales", tags=["behavior"]),
    get=extend_schema(summary="Obtener evaluación conductual", tags=["behavior"]),
    create=extend_schema(summary="Crear evaluación conductual", tags=["behavior"]),
    update=extend_schema(summary="Actualizar evaluación conductual", tags=["behavior"]),
    partial_update=extend_schema(summary="Actualizar evaluación parcialmente", tags=["behavior"]),
    destroy=extend_schema(summary="Eliminar evaluación conductual", tags=["behavior"]),
    related_incidents=extend_schema(summary="Incidentes relacionados", tags=["behavior"]),
)
class BehaviorEvaluationViewSet(BaseBehaviorViewSet):
    serializer_class = BehaviorEvaluationSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["enrollment", "academic_period"]
    search_fields = ["enrollment__student__user__person__names"]
    ordering_fields = ["evaluation_date", "created_at"]
    ordering = ["-evaluation_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = BehaviorEvaluationRepository()

    def get_queryset(self):
        qs = self.repository.get_all()
        return scope_student_to_enrollment(self.request, qs)

    def perform_create(self, serializer):
        data = serializer.validated_data
        obj = BehaviorEvaluationService.calculate_behavior_evaluation(
            enrollment=data["enrollment"],
            academic_period=data["academic_period"],
        )
        serializer.instance = obj

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        if "final_scale" in data:
            obj = BehaviorEvaluationService.override_evaluation(
                serializer.instance,
                new_scale=data.pop("final_scale"),
                reason=data.pop("override_reason", ""),
            )
        else:
            obj = serializer.instance
            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            obj.save()
        serializer.instance = obj

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
