"""
Vistas de API para el módulo Analytics.

Utiliza ViewSets de DRF para operaciones CRUD RESTful sobre
puntajes de riesgo y snapshots de características.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.constants.permissions import analytics
from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.api.permissions import HasPermission

from ..models import AlertType, EarlyAlert, RiskFactor, StudentRiskFactor, UrgencyLevel
from ..repositories import (
    AlertTypeRepository,
    EarlyAlertRepository,
    RiskFactorRepository,
    StudentFeatureSnapshotRepository,
    StudentRiskFactorRepository,
    StudentRiskScoreRepository,
    UrgencyLevelRepository,
)
from ..services.early_alert_service import EarlyAlertService
from .serializers import (
    AlertTypeSerializer,
    EarlyAlertSerializer,
    RiskFactorSerializer,
    StudentFeatureSnapshotSerializer,
    StudentRiskFactorSerializer,
    StudentRiskScoreSerializer,
    UrgencyLevelSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="Listar registros", tags=["analytics"]),
    retrieve=extend_schema(summary="Obtener registro", tags=["analytics"]),
)
class BaseAnalyticsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasPermission]
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e), status=400)

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


@extend_schema_view(
    list=extend_schema(summary="Listar tipos de alerta", tags=["analytics"]),
    retrieve=extend_schema(summary="Obtener tipo de alerta", tags=["analytics"]),
    create=extend_schema(summary="Crear tipo de alerta", tags=["analytics"]),
    update=extend_schema(summary="Actualizar tipo de alerta", tags=["analytics"]),
    partial_update=extend_schema(summary="Actualizar tipo de alerta parcialmente", tags=["analytics"]),
    destroy=extend_schema(summary="Eliminar tipo de alerta", tags=["analytics"]),
)
class AlertTypeViewSet(BaseAnalyticsViewSet):
    serializer_class = AlertTypeSerializer
    action_permissions = {
        "list": analytics.VIEW_ALERT_TYPE,
        "retrieve": analytics.VIEW_ALERT_TYPE,
        "create": analytics.CREATE_ALERT_TYPE,
        "update": analytics.UPDATE_ALERT_TYPE,
        "partial_update": analytics.UPDATE_ALERT_TYPE,
        "destroy": analytics.DELETE_ALERT_TYPE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = AlertTypeRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar niveles de urgencia", tags=["analytics"]),
    retrieve=extend_schema(summary="Obtener nivel de urgencia", tags=["analytics"]),
    create=extend_schema(summary="Crear nivel de urgencia", tags=["analytics"]),
    update=extend_schema(summary="Actualizar nivel de urgencia", tags=["analytics"]),
    partial_update=extend_schema(summary="Actualizar nivel de urgencia parcialmente", tags=["analytics"]),
    destroy=extend_schema(summary="Eliminar nivel de urgencia", tags=["analytics"]),
)
class UrgencyLevelViewSet(BaseAnalyticsViewSet):
    serializer_class = UrgencyLevelSerializer
    action_permissions = {
        "list": analytics.VIEW_URGENCY_LEVEL,
        "retrieve": analytics.VIEW_URGENCY_LEVEL,
        "create": analytics.CREATE_URGENCY_LEVEL,
        "update": analytics.UPDATE_URGENCY_LEVEL,
        "partial_update": analytics.UPDATE_URGENCY_LEVEL,
        "destroy": analytics.DELETE_URGENCY_LEVEL,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = UrgencyLevelRepository()

    def get_queryset(self):
        return self.repository.get_all()


class StudentRiskScoreViewSet(BaseAnalyticsViewSet):
    serializer_class = StudentRiskScoreSerializer
    action_permissions = {
        "list": analytics.VIEW_RISK_SCORE,
        "retrieve": analytics.VIEW_RISK_SCORE,
        "calculate": analytics.CREATE_STUDENT_RISK_FACTOR,
        "batch_calculate": analytics.CREATE_STUDENT_RISK_FACTOR,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = StudentRiskScoreRepository()

    def get_queryset(self):
        return self.repository.get_all()

    @action(detail=False, methods=["post"])
    def calculate(self, request):
        from apps.analytics.tasks import calculate_student_academic_risk_task

        student_id = request.data.get("student_id")
        academic_period_id = request.data.get("academic_period_id")
        if not student_id or not academic_period_id:
            return Response(
                "student_id y academic_period_id son requeridos", status=400
            )
        task = calculate_student_academic_risk_task.delay(
            student_id, academic_period_id
        )
        return Response({"task_id": task.id, "status": "PENDING"})

    @action(detail=False, methods=["post"])
    def batch_calculate(self, request):
        from apps.analytics.tasks import batch_calculate_academic_risk

        academic_period_id = request.data.get("academic_period_id")
        student_ids = request.data.get("student_ids")
        if not academic_period_id or not student_ids:
            return Response(
                "academic_period_id y student_ids son requeridos", status=400
            )
        task = batch_calculate_academic_risk.delay(academic_period_id, student_ids)
        return Response({"task_id": task.id, "status": "PENDING"})


class StudentFeatureSnapshotViewSet(BaseAnalyticsViewSet):
    serializer_class = StudentFeatureSnapshotSerializer
    action_permissions = {
        "list": analytics.VIEW_FEATURE_SNAPSHOT,
        "retrieve": analytics.VIEW_FEATURE_SNAPSHOT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = StudentFeatureSnapshotRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar factores de riesgo", tags=["analytics"]),
    retrieve=extend_schema(summary="Obtener factor de riesgo", tags=["analytics"]),
)
class RiskFactorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RiskFactorSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": analytics.VIEW_RISK_FACTOR,
        "retrieve": analytics.VIEW_RISK_FACTOR,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = RiskFactorRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar factores por estudiante", tags=["analytics"]),
    retrieve=extend_schema(summary="Obtener factor de estudiante", tags=["analytics"]),
)
class StudentRiskFactorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentRiskFactorSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": analytics.VIEW_STUDENT_RISK_FACTOR,
        "retrieve": analytics.VIEW_STUDENT_RISK_FACTOR,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = StudentRiskFactorRepository()

    def get_queryset(self):
        return self.repository.get_all()


@extend_schema_view(
    list=extend_schema(summary="Listar alertas tempranas", tags=["analytics"]),
    retrieve=extend_schema(summary="Obtener alerta temprana", tags=["analytics"]),
    create=extend_schema(summary="Crear alerta temprana", tags=["analytics"]),
    update=extend_schema(summary="Actualizar alerta temprana", tags=["analytics"]),
    partial_update=extend_schema(
        summary="Actualizar alerta parcialmente", tags=["analytics"]
    ),
    destroy=extend_schema(summary="Eliminar alerta temprana", tags=["analytics"]),
    mark_attended=extend_schema(
        summary="Marcar alerta como atendida", tags=["analytics"]
    ),
)
class EarlyAlertViewSet(viewsets.ModelViewSet):
    serializer_class = EarlyAlertSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": analytics.VIEW_EARLY_ALERT,
        "retrieve": analytics.VIEW_EARLY_ALERT,
        "create": analytics.CREATE_EARLY_ALERT,
        "update": analytics.UPDATE_EARLY_ALERT,
        "partial_update": analytics.UPDATE_EARLY_ALERT,
        "destroy": analytics.DELETE_EARLY_ALERT,
        "mark_attended": analytics.UPDATE_EARLY_ALERT,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = EarlyAlertRepository()

    def get_queryset(self):
        return self.repository.get_all()

    @action(detail=True, methods=["post"])
    def mark_attended(self, request, pk=None):
        alert = self.get_object()
        actions = request.data.get("response_actions", "")
        alert = EarlyAlertService.mark_as_attended(alert.id, request.user.id, actions)
        if alert:
            return Response(EarlyAlertSerializer(alert).data)
        return Response("Alerta no encontrada", status=400)
