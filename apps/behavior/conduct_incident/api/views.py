from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.behavior.api.base import BaseBehaviorViewSet
from apps.core.api.scoping import scope_student_to_enrollment

from ..application.serializers import ConductIncidentSerializer
from ..domain.services import ConductIncidentService
from ..infrastructure.repositories import ConductIncidentRepository
from ..permissions import ACTION_PERMISSIONS


@extend_schema_view(
    list=extend_schema(summary="Listar incidentes", tags=["behavior"]),
    get=extend_schema(summary="Obtener incidente", tags=["behavior"]),
    create=extend_schema(summary="Crear incidente", tags=["behavior"]),
    update=extend_schema(summary="Actualizar incidente", tags=["behavior"]),
    partial_update=extend_schema(summary="Actualizar incidente parcialmente", tags=["behavior"]),
    destroy=extend_schema(summary="Eliminar incidente", tags=["behavior"]),
)
class ConductIncidentViewSet(BaseBehaviorViewSet):
    serializer_class = ConductIncidentSerializer
    action_permissions = ACTION_PERMISSIONS
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["enrollment"]
    search_fields = ["enrollment__student__user__person__names", "description"]
    ordering_fields = ["incident_date", "created_at"]
    ordering = ["-incident_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = ConductIncidentRepository()

    def get_queryset(self):
        qs = self.repository.get_all()
        return scope_student_to_enrollment(self.request, qs)

    def perform_create(self, serializer):
        data = serializer.validated_data
        obj = ConductIncidentService.create_conduct_incident(
            incident_type=data["incident_type"],
            severity=data["severity"],
            academic_period=data["academic_period"],
            enrollment=data["enrollment"],
            incident_date=data["incident_date"],
            description=data.get("description", ""),
            actions_taken=data.get("actions_taken", ""),
            family_notified=data.get("family_notified", False),
        )
        serializer.instance = obj

    def perform_update(self, serializer):
        data = dict(serializer.validated_data)
        obj = ConductIncidentService.update_conduct_incident(serializer.instance.id, **data)
        serializer.instance = obj
