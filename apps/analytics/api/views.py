"""
Vistas de API para el módulo Analytics.

Utiliza ViewSets de DRF para operaciones CRUD RESTful sobre
puntajes de riesgo y snapshots de características.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.constants.permissions import analytics
from apps.core.pagination import StandardResultsSetPagination
from apps.core.permissions import HasPermission
from apps.core.utils import ok_response, error_response

from ..models import RiskFactor, StudentRiskFactor
from ..repositories import (
    StudentFeatureSnapshotRepository,
    StudentRiskScoreRepository,
)
from .serializers import (
    RiskFactorSerializer,
    StudentFeatureSnapshotSerializer,
    StudentRiskFactorSerializer,
    StudentRiskScoreSerializer,
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
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return ok_response(serializer.data)
        except Exception as e:
            return error_response(e)

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


class StudentRiskScoreViewSet(BaseAnalyticsViewSet):
    serializer_class = StudentRiskScoreSerializer
    action_permissions = {
        "list": analytics.VIEW_RISK_SCORE,
        "retrieve": analytics.VIEW_RISK_SCORE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = StudentRiskScoreRepository()

    def get_queryset(self):
        return self.repository.get_all()


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


class RiskFactorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RiskFactorSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": analytics.VIEW_RISK_FACTOR,
        "retrieve": analytics.VIEW_RISK_FACTOR,
    }

    def get_queryset(self):
        return RiskFactor.objects.all().order_by("name")

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


class StudentRiskFactorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentRiskFactorSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": analytics.VIEW_STUDENT_RISK_FACTOR,
        "retrieve": analytics.VIEW_STUDENT_RISK_FACTOR,
    }

    def get_queryset(self):
        return StudentRiskFactor.objects.all().select_related(
            "student_risk_score", "risk_factor"
        )
