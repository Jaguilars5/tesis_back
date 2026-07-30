from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.behavior.api.base import BaseBehaviorViewSet
from apps.behavior.conduct_incident.infrastructure.repositories import (
    ConductIncidentRepository,
)
from apps.core.api.scoping import scope_student_to_enrollment
from apps.core.utils import ok_response, error_response

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
    calculate=extend_schema(summary="Calcular evaluación conductual", tags=["behavior"]),
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

    def get_queryset(self):
        qs = BehaviorEvaluationRepository.get_all(active_only=False)
        return scope_student_to_enrollment(self.request, qs)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            obj = BehaviorEvaluationService.calculate_behavior_evaluation(
                enrollment_id=data["enrollment"].id,
                academic_period_id=data["academic_period"].id,
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

    def perform_update(self, serializer):
        data = serializer.validated_data
        try:
            obj = BehaviorEvaluationService.update_evaluation(
                pk=serializer.instance.id,
                final_scale_id=data.get("final_scale").id if data.get("final_scale") else None,
                override_reason=data.get("override_reason", ""),
                general_observation=data.get("general_observation", ""),
                evaluation_date=data.get("evaluation_date"),
            )
            serializer.instance = obj
        except ValueError as e:
            raise ValidationError(e.args[0] if e.args else str(e))

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
        if not academic_period_id:
            return error_response(
                "academic_period_id es requerido",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            if not enrollment_id or enrollment_id == "all":
                from apps.academic.academic_period.infrastructure.models import AcademicPeriod
                from apps.students.infrastructure.models import Enrollment, EnrollmentStatusChoices

                period = AcademicPeriod.objects.get(id=academic_period_id)
                enrollments = Enrollment.objects.filter(
                    section__school_year_id=period.school_year_id,
                    enrollment_status=EnrollmentStatusChoices.ACTIVE,
                ).values_list("id", flat=True)
                evaluations = [
                    BehaviorEvaluationService.calculate_behavior_evaluation(
                        enrollment_id=enrollment,
                        academic_period_id=academic_period_id,
                    )
                    for enrollment in enrollments
                ]
                serializer = self.get_serializer(evaluations, many=True)
                return ok_response(
                    {"count": len(evaluations), "results": serializer.data}
                )

            evaluation = BehaviorEvaluationService.calculate_behavior_evaluation(
                enrollment_id=enrollment_id,
                academic_period_id=academic_period_id,
            )
            serializer = self.get_serializer(evaluation)
            return ok_response(serializer.data)
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def related_incidents(self, request, pk=None):
        evaluation = self.get_object()
        incidents = ConductIncidentRepository.get_by_enrollment_and_period(
            enrollment_id=evaluation.enrollment_id,
            academic_period_id=evaluation.academic_period_id,
        )
        data = [
            {
                "id": inc.id,
                "severity": inc.severity.name if inc.severity else None,
                "incident_type": inc.incident_type.name if inc.incident_type else None,
                "description": inc.description,
                "incident_date": inc.incident_date,
                "status": inc.status,
            }
            for inc in incidents
        ]
        return ok_response(data)
