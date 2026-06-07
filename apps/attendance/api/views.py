from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.attendance.api.serializers import (
    AttendanceSerializer, AttendanceStatusSerializer, IncidentTypeSerializer,
    ConductIncidentSerializer, SocioemotionalSkillSerializer,
    SkillEvaluationSerializer, BehaviorEvaluationSerializer,
)
from apps.attendance.repositories import (
    AttendanceRepository,
    ConductIncidentRepository,
    AttendanceStatusRepository,
    IncidentTypeRepository,
    SocioemotionalSkillRepository,
    SkillEvaluationRepository,
    BehaviorEvaluationRepository,
)
from apps.core.api.permissions import HasPermission
from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.constants.permissions import attendance as perm


@extend_schema_view(
    list=extend_schema(summary="Listar asistencias", tags=["attendance"]),
    retrieve=extend_schema(summary="Obtener asistencia", tags=["attendance"]),
    create=extend_schema(summary="Registrar asistencia", tags=["attendance"]),
    update=extend_schema(summary="Actualizar asistencia", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar asistencia parcialmente", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar asistencia", tags=["attendance"]),
)
class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_ATTENDANCE,
        "retrieve": perm.VIEW_ATTENDANCE,
        "create": perm.CREATE_ATTENDANCE,
        "update": perm.UPDATE_ATTENDANCE,
        "partial_update": perm.UPDATE_ATTENDANCE,
        "destroy": perm.DELETE_ATTENDANCE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AttendanceRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar incidentes", tags=["attendance"]),
    retrieve=extend_schema(summary="Obtener incidente", tags=["attendance"]),
    create=extend_schema(summary="Crear incidente", tags=["attendance"]),
    update=extend_schema(summary="Actualizar incidente", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar incidente parcialmente", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar incidente", tags=["attendance"]),
)
class ConductIncidentViewSet(viewsets.ModelViewSet):
    serializer_class = ConductIncidentSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_CONDUCT_INCIDENT,
        "retrieve": perm.VIEW_CONDUCT_INCIDENT,
        "create": perm.CREATE_CONDUCT_INCIDENT,
        "update": perm.UPDATE_CONDUCT_INCIDENT,
        "partial_update": perm.UPDATE_CONDUCT_INCIDENT,
        "destroy": perm.DELETE_CONDUCT_INCIDENT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = ConductIncidentRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar evaluaciones conductuales", tags=["attendance"]),
    retrieve=extend_schema(summary="Obtener evaluación conductual", tags=["attendance"]),
    create=extend_schema(summary="Crear evaluación conductual", tags=["attendance"]),
    update=extend_schema(summary="Actualizar evaluación conductual", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar evaluación parcialmente", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar evaluación conductual", tags=["attendance"]),
)
class BehaviorEvaluationViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorEvaluationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_BEHAVIOR_EVALUATION,
        "retrieve": perm.VIEW_BEHAVIOR_EVALUATION,
        "create": perm.CREATE_BEHAVIOR_EVALUATION,
        "update": perm.UPDATE_BEHAVIOR_EVALUATION,
        "partial_update": perm.UPDATE_BEHAVIOR_EVALUATION,
        "destroy": perm.DELETE_BEHAVIOR_EVALUATION,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = BehaviorEvaluationRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de incidente", tags=["attendance"]),
    retrieve=extend_schema(summary="Obtener tipo de incidente", tags=["attendance"]),
    create=extend_schema(summary="Crear tipo de incidente", tags=["attendance"]),
    update=extend_schema(summary="Actualizar tipo de incidente", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar tipo parcialmente", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar tipo de incidente", tags=["attendance"]),
)
class IncidentTypeViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentTypeSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_INCIDENT_TYPE,
        "retrieve": perm.VIEW_INCIDENT_TYPE,
        "create": perm.CREATE_INCIDENT_TYPE,
        "update": perm.UPDATE_INCIDENT_TYPE,
        "partial_update": perm.UPDATE_INCIDENT_TYPE,
        "destroy": perm.DELETE_INCIDENT_TYPE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = IncidentTypeRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar habilidades socioemocionales", tags=["attendance"]),
    retrieve=extend_schema(summary="Obtener habilidad socioemocional", tags=["attendance"]),
    create=extend_schema(summary="Crear habilidad socioemocional", tags=["attendance"]),
    update=extend_schema(summary="Actualizar habilidad socioemocional", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar habilidad parcialmente", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar habilidad socioemocional", tags=["attendance"]),
)
class SocioemotionalSkillViewSet(viewsets.ModelViewSet):
    serializer_class = SocioemotionalSkillSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_SOCIOEMOTIONAL_SKILL,
        "retrieve": perm.VIEW_SOCIOEMOTIONAL_SKILL,
        "create": perm.CREATE_SOCIOEMOTIONAL_SKILL,
        "update": perm.UPDATE_SOCIOEMOTIONAL_SKILL,
        "partial_update": perm.UPDATE_SOCIOEMOTIONAL_SKILL,
        "destroy": perm.DELETE_SOCIOEMOTIONAL_SKILL,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SocioemotionalSkillRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar evaluaciones de habilidades", tags=["attendance"]),
    retrieve=extend_schema(summary="Obtener evaluación de habilidad", tags=["attendance"]),
    create=extend_schema(summary="Crear evaluación de habilidad", tags=["attendance"]),
    update=extend_schema(summary="Actualizar evaluación de habilidad", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar evaluación parcialmente", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar evaluación de habilidad", tags=["attendance"]),
)
class SkillEvaluationViewSet(viewsets.ModelViewSet):
    serializer_class = SkillEvaluationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_SKILL_EVALUATION,
        "retrieve": perm.VIEW_SKILL_EVALUATION,
        "create": perm.CREATE_SKILL_EVALUATION,
        "update": perm.UPDATE_SKILL_EVALUATION,
        "partial_update": perm.UPDATE_SKILL_EVALUATION,
        "destroy": perm.DELETE_SKILL_EVALUATION,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = SkillEvaluationRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar estados de asistencia", tags=["attendance"]),
    retrieve=extend_schema(summary="Obtener estado de asistencia", tags=["attendance"]),
    create=extend_schema(summary="Crear estado de asistencia", tags=["attendance"]),
    update=extend_schema(summary="Actualizar estado de asistencia", tags=["attendance"]),
    partial_update=extend_schema(summary="Actualizar estado parcialmente", tags=["attendance"]),
    destroy=extend_schema(summary="Eliminar estado de asistencia", tags=["attendance"]),
)
class AttendanceStatusViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceStatusSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_ATTENDANCE_STATUS,
        "retrieve": perm.VIEW_ATTENDANCE_STATUS,
        "create": perm.CREATE_ATTENDANCE_STATUS,
        "update": perm.UPDATE_ATTENDANCE_STATUS,
        "partial_update": perm.UPDATE_ATTENDANCE_STATUS,
        "destroy": perm.DELETE_ATTENDANCE_STATUS,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AttendanceStatusRepository()

    def get_queryset(self):
        return self.repository.get_all()
