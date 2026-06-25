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
from apps.core.utils import ok_response, error_response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from ..models import RiskFactor, StudentRiskFactor
from ..repositories import (
    RiskFactorRepository,
    RiskScoringConfigRepository,
    StudentFeatureSnapshotRepository,
    StudentRiskFactorRepository,
    StudentRiskScoreRepository,
)
from ..services.dashboard_service import DashboardService
from ..services.csv_export_service import CSVExportService
from ..services.risk_scoring_config_service import PRESETS, RiskScoringConfigService
from django.http import HttpResponse
from .filters import StudentFeatureSnapshotFilter, StudentRiskScoreFilter
from .serializers import (
    RiskFactorSerializer,
    RiskScoringConfigSerializer,
    SimulateRiskInputSerializer,
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

class StudentRiskScoreViewSet(BaseAnalyticsViewSet):
    serializer_class = StudentRiskScoreSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentRiskScoreFilter
    search_fields = ["enrollment__student__user__person__names"]
    ordering_fields = ["risk_score", "calculated_at", "risk_label"]
    ordering = ["-calculated_at"]
    action_permissions = {
        "list": analytics.VIEW_RISK_SCORE,
        "retrieve": analytics.VIEW_RISK_SCORE,
        "calculate": analytics.CREATE_STUDENT_RISK_FACTOR,
        "batch_calculate": analytics.CREATE_STUDENT_RISK_FACTOR,
        "simulate": analytics.VIEW_RISK_SCORE,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = StudentRiskScoreRepository()

    def get_queryset(self):
        qs = self.repository.get_all()
        user = self.request.user
        if user.is_authenticated and user.user_roles.filter(role__code="DOCENTE").exists():
            qs = qs.filter(
                enrollment__section__subject_offerings__teacher_assignments__user=user,
                enrollment__section__subject_offerings__teacher_assignments__is_active=True,
            ).distinct()
        return qs

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

    @action(detail=False, methods=["post"])
    def simulate(self, request):
        from apps.analytics.tasks import calculate_academic_risk, _predict_ml_score

        serializer = SimulateRiskInputSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(msg="Parámetros inválidos", data=serializer.errors)

        params = serializer.validated_data

        variables = {
            "conducta": {
                "faltas_leves": params["mild_incidents_count"],
                "faltas_graves": params["severe_incidents_count"],
            },
            "asistencia": {
                "porcentaje_asistencia": params["attendance_rate"],
                "total_registros": 1,
            },
            "calificaciones": {
                "promedio_actual": params["average_grade"],
                "total_calificaciones": 1,
                "materias_reprobadas": params["failing_subjects_count"],
            },
        }

        snapshot = {
            "estudiante_id": "simulacion",
            "periodo": "simulacion",
            "variables": variables,
        }

        config = RiskScoringConfigService.get_effective()
        config_serializer = RiskScoringConfigSerializer(config)

        rules_result = calculate_academic_risk(snapshot)

        ml_result = None
        if params.get("try_ml"):
            try:
                ml_score = _predict_ml_score(snapshot)
                if ml_score is not None:
                    ml_result = {
                        "puntaje_riesgo": round(float(ml_score), 2),
                        "model_version": "sklearn-joblib-v2",
                    }
            except Exception:
                ml_result = {"error": "Error al ejecutar modelo ML"}

        return ok_response({
            "reglas": {
                "semaforo_riesgo": rules_result["semaforo_riesgo"],
                "detalle_por_variable": rules_result["detalle_por_variable"],
                "model_version": rules_result["model_version"],
            },
            "ml": ml_result,
            "config_usada": config_serializer.data,
        })


class StudentFeatureSnapshotViewSet(BaseAnalyticsViewSet):
    serializer_class = StudentFeatureSnapshotSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentFeatureSnapshotFilter
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
    overview=extend_schema(summary="KPIs globales del período", tags=["analytics"]),
    risk_distribution=extend_schema(summary="Distribución semáforo por grado", tags=["analytics"]),
    students_at_risk=extend_schema(summary="Estudiantes en nivel de riesgo", tags=["analytics"]),
    export_csv=extend_schema(summary="Exportar CSV", tags=["analytics"]),
    section_summary=extend_schema(summary="Resumen de sección", tags=["analytics"]),
    enrollment_trend=extend_schema(summary="Tendencia de matrículas por mes", tags=["analytics"]),
)
class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "overview": analytics.VIEW_RISK_SCORE,
        "risk_distribution": analytics.VIEW_RISK_SCORE,
        "risk_by_city": analytics.VIEW_RISK_SCORE,
        "risk_by_special_needs": analytics.VIEW_RISK_SCORE,
        "dropout_by_city": analytics.VIEW_RISK_SCORE,
        "withdrawal_reasons": analytics.VIEW_RISK_SCORE,
        "students_at_risk": analytics.VIEW_RISK_SCORE,
        "export_csv": analytics.VIEW_RISK_SCORE,
        "section_summary": analytics.VIEW_RISK_SCORE,
        "enrollment_trend": analytics.VIEW_RISK_SCORE,
        "recalculate_period": analytics.CREATE_STUDENT_RISK_FACTOR,
    }

    @action(detail=False, methods=["get"])
    def overview(self, request):
        period_id = request.query_params.get("period_id")
        if not period_id:
            return Response("period_id es requerido", status=400)
        data = DashboardService.get_overview(period_id)
        return Response(data)

    @action(detail=False, methods=["get"])
    def risk_distribution(self, request):
        period_id = request.query_params.get("period_id")
        if not period_id:
            return Response("period_id es requerido", status=400)
        data = DashboardService.get_risk_distribution_by_grade(period_id)
        return Response(data)

    @action(detail=False, methods=["get"])
    def risk_by_city(self, request):
        period_id = request.query_params.get("period_id")
        if not period_id:
            return Response("period_id es requerido", status=400)
        data = DashboardService.get_risk_distribution_by_city(period_id)
        return Response(data)

    @action(detail=False, methods=["get"])
    def risk_by_special_needs(self, request):
        period_id = request.query_params.get("period_id")
        if not period_id:
            return Response("period_id es requerido", status=400)
        data = DashboardService.get_risk_distribution_by_special_needs_type(period_id)
        return Response(data)

    @action(detail=False, methods=["get"])
    def dropout_by_city(self, request):
        school_year_id = request.query_params.get("school_year_id")
        data = DashboardService.get_dropout_by_city(school_year_id)
        return Response(data)

    @action(detail=False, methods=["get"])
    def withdrawal_reasons(self, request):
        school_year_id = request.query_params.get("school_year_id")
        data = DashboardService.get_withdrawal_reasons(school_year_id)
        return Response(data)

    @action(detail=False, methods=["get"])
    def students_at_risk(self, request):
        period_id = request.query_params.get("period_id")
        risk_label = request.query_params.get("risk_label", "rojo")
        if not period_id:
            return Response("period_id es requerido", status=400)
        data = DashboardService.get_students_at_risk(period_id, risk_label)
        return Response(data)

    @action(detail=False, methods=["get"])
    def export_csv(self, request):
        export_type = request.query_params.get("type")
        period_id = request.query_params.get("period_id")
        if not export_type or not period_id:
            return Response("type y period_id son requeridos", status=400)
        try:
            csv_data = CSVExportService.generate_csv(export_type, period_id)
            response = HttpResponse(csv_data, content_type="text/csv")
            response["Content-Disposition"] = f'attachment; filename="{export_type}_{period_id}.csv"'
            return response
        except ValueError as e:
            return Response(str(e), status=400)

    @action(detail=False, methods=["get"])
    def section_summary(self, request):
        section_id = request.query_params.get("section_id")
        if not section_id:
            return Response("section_id es requerido", status=400)
        from django.db.models import Avg
        from ..models import StudentFeatureSnapshot, StudentRiskScore
        snapshots = StudentFeatureSnapshot.objects.filter(
            enrollment__section_id=section_id
        )
        scores = StudentRiskScore.objects.filter(
            enrollment__section_id=section_id
        )
        return Response({
            "section_id": section_id,
            "total_students": snapshots.count(),
            "attendance_rate_avg": snapshots.aggregate(Avg("attendance_rate"))["attendance_rate__avg"] or 0,
            "formative_avg": snapshots.aggregate(Avg("formative_avg_normalized"))["formative_avg_normalized__avg"] or 0,
            "risk_distribution": {
                "rojo": scores.filter(risk_label="rojo").count(),
                "amarillo": scores.filter(risk_label="amarillo").count(),
                "verde": scores.filter(risk_label="verde").count(),
            },
        })

    @action(detail=False, methods=["get"])
    def enrollment_trend(self, request):
        school_year_id = request.query_params.get("school_year_id")
        data = DashboardService.get_enrollment_trend(school_year_id)
        return Response(data)

    @action(detail=False, methods=["post"])
    def recalculate_period(self, request):
        from apps.analytics.tasks import batch_calculate_academic_risk
        from apps.students.models import Enrollment

        period_id = request.data.get("academic_period_id")
        if not period_id:
            return Response("academic_period_id es requerido", status=400)

        student_ids = list(
            Enrollment.objects.filter(
                enrollment_status="ACT",
                section__school_year__academic_periods__id=period_id,
            ).values_list("student_id", flat=True)
        )

        if not student_ids:
            return Response({"task_id": None, "status": "NO_STUDENTS"})

        task = batch_calculate_academic_risk.delay(period_id, student_ids, user_id=request.user.id)
        return Response({"task_id": task.id, "status": "PENDING"})


@extend_schema_view(
    list=extend_schema(summary="Obtener configuración del motor de riesgo", tags=["analytics"]),
    update_config=extend_schema(summary="Actualizar configuración del motor de riesgo", tags=["analytics"]),
    apply_preset=extend_schema(summary="Aplicar un preset de configuración", tags=["analytics"]),
)
class RiskScoringConfigViewSet(viewsets.ViewSet):
    """
    Configuración GLOBAL (singleton) del motor de riesgo académico (Fase 5).

    - GET   `/scoring-config/`               → configuración actual (defaults si no existe)
    - PATCH `/scoring-config/update_config/`  → actualizar pesos/umbrales/motor
    - POST  `/scoring-config/apply_preset/`   → aplicar preset Conservador/Equilibrado/Estricto
    """

    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": analytics.VIEW_SCORING_CONFIG,
        "update_config": analytics.UPDATE_SCORING_CONFIG,
        "apply_preset": analytics.UPDATE_SCORING_CONFIG,
    }

    def list(self, request):
        config = RiskScoringConfigRepository.get_or_create_singleton()
        return Response(RiskScoringConfigSerializer(config).data)

    @action(detail=False, methods=["patch"])
    def update_config(self, request):
        config = RiskScoringConfigRepository.get_or_create_singleton()
        serializer = RiskScoringConfigSerializer(
            config, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def apply_preset(self, request):
        preset = request.data.get("preset")
        if preset not in PRESETS:
            return Response(
                f"Preset inválido. Opciones: {', '.join(PRESETS.keys())}",
                status=400,
            )
        config = RiskScoringConfigRepository.get_or_create_singleton()
        payload = {**PRESETS[preset], "preset": preset}
        serializer = RiskScoringConfigSerializer(config, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
