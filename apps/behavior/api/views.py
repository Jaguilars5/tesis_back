from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.behavior.api.serializers import (
    BehaviorEvaluationSerializer,
    ConductIncidentSerializer,
    DiagnosticEvaluationSerializer,
    IncidentTypeSerializer,
    SkillEvaluationSerializer,
    SocioemotionalSkillSerializer,
)
from apps.behavior.repositories import (
    BehaviorEvaluationRepository,
    ConductIncidentRepository,
    DiagnosticEvaluationRepository,
    IncidentTypeRepository,
    SkillEvaluationRepository,
    SocioemotionalSkillRepository,
)
from apps.core.api.permissions import HasPermission
from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.constants.permissions import behavior


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
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar evaluaciones conductuales", tags=["behavior"]),
    retrieve=extend_schema(summary="Obtener evaluación conductual", tags=["behavior"]),
    create=extend_schema(summary="Crear evaluación conductual", tags=["behavior"]),
    update=extend_schema(summary="Actualizar evaluación conductual", tags=["behavior"]),
    partial_update=extend_schema(summary="Actualizar evaluación parcialmente", tags=["behavior"]),
    destroy=extend_schema(summary="Eliminar evaluación conductual", tags=["behavior"]),
)
class BehaviorEvaluationViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorEvaluationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": behavior.VIEW_BEHAVIOR_EVALUATION,
        "retrieve": behavior.VIEW_BEHAVIOR_EVALUATION,
        "create": behavior.CREATE_BEHAVIOR_EVALUATION,
        "update": behavior.UPDATE_BEHAVIOR_EVALUATION,
        "partial_update": behavior.UPDATE_BEHAVIOR_EVALUATION,
        "destroy": behavior.DELETE_BEHAVIOR_EVALUATION,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = BehaviorEvaluationRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar habilidades socioemocionales", tags=["behavior"]),
    retrieve=extend_schema(summary="Obtener habilidad socioemocional", tags=["behavior"]),
    create=extend_schema(summary="Crear habilidad socioemocional", tags=["behavior"]),
    update=extend_schema(summary="Actualizar habilidad socioemocional", tags=["behavior"]),
    partial_update=extend_schema(summary="Actualizar habilidad parcialmente", tags=["behavior"]),
    destroy=extend_schema(summary="Eliminar habilidad socioemocional", tags=["behavior"]),
)
class SocioemotionalSkillViewSet(viewsets.ModelViewSet):
    serializer_class = SocioemotionalSkillSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": behavior.VIEW_SOCIOEMOTIONAL_SKILL,
        "retrieve": behavior.VIEW_SOCIOEMOTIONAL_SKILL,
        "create": behavior.CREATE_SOCIOEMOTIONAL_SKILL,
        "update": behavior.UPDATE_SOCIOEMOTIONAL_SKILL,
        "partial_update": behavior.UPDATE_SOCIOEMOTIONAL_SKILL,
        "destroy": behavior.DELETE_SOCIOEMOTIONAL_SKILL,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SocioemotionalSkillRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar evaluaciones de habilidades", tags=["behavior"]),
    retrieve=extend_schema(summary="Obtener evaluación de habilidad", tags=["behavior"]),
    create=extend_schema(summary="Crear evaluación de habilidad", tags=["behavior"]),
    update=extend_schema(summary="Actualizar evaluación de habilidad", tags=["behavior"]),
    partial_update=extend_schema(summary="Actualizar evaluación parcialmente", tags=["behavior"]),
    destroy=extend_schema(summary="Eliminar evaluación de habilidad", tags=["behavior"]),
)
class SkillEvaluationViewSet(viewsets.ModelViewSet):
    serializer_class = SkillEvaluationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": behavior.VIEW_SKILL_EVALUATION,
        "retrieve": behavior.VIEW_SKILL_EVALUATION,
        "create": behavior.CREATE_SKILL_EVALUATION,
        "update": behavior.UPDATE_SKILL_EVALUATION,
        "partial_update": behavior.UPDATE_SKILL_EVALUATION,
        "destroy": behavior.DELETE_SKILL_EVALUATION,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SkillEvaluationRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar evaluaciones diagnósticas", tags=["behavior"]),
    retrieve=extend_schema(summary="Obtener evaluación diagnóstica", tags=["behavior"]),
    create=extend_schema(summary="Crear evaluación diagnóstica", tags=["behavior"]),
    update=extend_schema(summary="Actualizar evaluación diagnóstica", tags=["behavior"]),
    partial_update=extend_schema(summary="Actualizar evaluación parcialmente", tags=["behavior"]),
    destroy=extend_schema(summary="Eliminar evaluación diagnóstica", tags=["behavior"]),
)
class DiagnosticEvaluationViewSet(viewsets.ModelViewSet):
    serializer_class = DiagnosticEvaluationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": behavior.VIEW_DIAGNOSTIC_EVALUATION,
        "retrieve": behavior.VIEW_DIAGNOSTIC_EVALUATION,
        "create": behavior.CREATE_DIAGNOSTIC_EVALUATION,
        "update": behavior.UPDATE_DIAGNOSTIC_EVALUATION,
        "partial_update": behavior.UPDATE_DIAGNOSTIC_EVALUATION,
        "destroy": behavior.DELETE_DIAGNOSTIC_EVALUATION,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = DiagnosticEvaluationRepository()

    def get_queryset(self):
        return self.repository.get_all()


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
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = IncidentTypeRepository()

    def get_queryset(self):
        return self.repository.get_all()
