"""
ViewSets de API para riesgo estudiantil.

Usa BaseAnalyticsViewSet para respuestas estandarizadas.
"""

from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.analytics.api.base import BaseAnalyticsViewSet
from apps.core.utils import ok_response, error_response

from ..permissions import (
    RISK_SCORE_ACTION_PERMISSIONS,
    RISK_FACTOR_ACTION_PERMISSIONS,
    STUDENT_RISK_FACTOR_ACTION_PERMISSIONS,
    FEATURE_SNAPSHOT_ACTION_PERMISSIONS,
    SCORING_CONFIG_ACTION_PERMISSIONS,
)
from ..application.serializers import (
    ApplyPresetSerializer,
    RiskFactorSerializer,
    RiskScoringConfigSerializer,
    SimulateRiskInputSerializer,
    StudentFeatureSnapshotSerializer,
    StudentRiskFactorSerializer,
    StudentRiskScoreSerializer,
)
from ..infrastructure.repositories import (
    RiskFactorRepository,
    StudentRiskScoreRepository,
    StudentRiskFactorRepository,
    StudentFeatureSnapshotRepository,
    RiskScoringConfigRepository,
)
from ..domain import risk_engine
from ..domain.services import StudentRiskCalculationService, RiskScoringConfigService


def _raise_validation_error(exc: ValueError) -> None:
    """Convierte ValueError con dict de errores a DRF ValidationError."""
    errors = (
        exc.args[0]
        if exc.args and isinstance(exc.args[0], dict)
        else {"non_field_errors": str(exc)}
    )
    raise DRFValidationError(errors) from exc


# ─────────────────────────────────────────────────────────────────────────────
# RiskFactor ViewSet (Read-only)
# ─────────────────────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(summary="Listar factores de riesgo", tags=["analytics"]),
    get=extend_schema(summary="Obtener factor de riesgo", tags=["analytics"]),
)
class RiskFactorViewSet(BaseAnalyticsViewSet):
    """ViewSet de solo lectura para catálogo de factores de riesgo."""

    serializer_class = RiskFactorSerializer
    action_permissions = RISK_FACTOR_ACTION_PERMISSIONS
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["code", "name"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = RiskFactorRepository()

    def get_queryset(self):
        return self.repository.get_all()

    # Readonly: remove create/update/destroy methods
    def create(self, request, *args, **kwargs):
        return error_response("Operación no permitida", status_code=405)

    def update(self, request, *args, **kwargs):
        return error_response("Operación no permitida", status_code=405)

    def destroy(self, request, *args, **kwargs):
        return error_response("Operación no permitida", status_code=405)


# ─────────────────────────────────────────────────────────────────────────────
# StudentRiskFactor ViewSet (Read-only)
# ─────────────────────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        summary="Listar factores de riesgo por estudiante", tags=["analytics"]
    ),
    get=extend_schema(
        summary="Obtener factor de riesgo de estudiante", tags=["analytics"]
    ),
)
class StudentRiskFactorViewSet(BaseAnalyticsViewSet):
    """ViewSet de solo lectura para factores de riesgo por estudiante."""

    serializer_class = StudentRiskFactorSerializer
    action_permissions = STUDENT_RISK_FACTOR_ACTION_PERMISSIONS
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = None  # StudentRiskFactorFilter si se necesita
    ordering_fields = ["contribution_weight", "created_at"]
    ordering = ["-contribution_weight"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = StudentRiskFactorRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def create(self, request, *args, **kwargs):
        return error_response("Operación no permitida", status_code=405)

    def update(self, request, *args, **kwargs):
        return error_response("Operación no permitida", status_code=405)

    def destroy(self, request, *args, **kwargs):
        return error_response("Operación no permitida", status_code=405)


# ─────────────────────────────────────────────────────────────────────────────
# StudentFeatureSnapshot ViewSet
# ─────────────────────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(summary="Listar snapshots de features", tags=["analytics"]),
    get=extend_schema(summary="Obtener snapshot de features", tags=["analytics"]),
    create=extend_schema(summary="Crear snapshot de features", tags=["analytics"]),
)
class StudentFeatureSnapshotViewSet(BaseAnalyticsViewSet):
    """ViewSet para snapshots de features de estudiantes."""

    serializer_class = StudentFeatureSnapshotSerializer
    action_permissions = FEATURE_SNAPSHOT_ACTION_PERMISSIONS
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = None  # StudentFeatureSnapshotFilter
    search_fields = ["enrollment__student__user__person__names"]
    ordering_fields = [
        "calculated_at",
        "risk_score",
        "attendance_rate",
        "failing_subjects_count",
    ]
    ordering = ["-calculated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = StudentFeatureSnapshotRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def perform_create(self, serializer):
        """Crea el snapshot a través del repositorio."""
        data = serializer.validated_data
        try:
            snapshot = StudentFeatureSnapshotRepository.create(**data)
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = snapshot

    # No permitir update/destroy directos (se crean automáticamente)
    def update(self, request, *args, **kwargs):
        return error_response("Los snapshots no pueden modificarse", status_code=405)

    def destroy(self, request, *args, **kwargs):
        return error_response("Los snapshots no pueden eliminarse", status_code=405)


# ─────────────────────────────────────────────────────────────────────────────
# StudentRiskScore ViewSet
# ─────────────────────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(summary="Listar puntajes de riesgo", tags=["analytics"]),
    get=extend_schema(summary="Obtener puntaje de riesgo", tags=["analytics"]),
    create=extend_schema(summary="Crear puntaje de riesgo", tags=["analytics"]),
    calculate=extend_schema(
        summary="Calcular riesgo para un estudiante (async)", tags=["analytics"]
    ),
    batch_calculate=extend_schema(
        summary="Calcular riesgo en batch (async)", tags=["analytics"]
    ),
)
class StudentRiskScoreViewSet(BaseAnalyticsViewSet):
    """
    ViewSet para puntajes de riesgo de estudiantes.

    Proporciona lectura y acciones para calcular riesgo asíncronamente.
    """

    serializer_class = StudentRiskScoreSerializer
    action_permissions = RISK_SCORE_ACTION_PERMISSIONS
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = None  # StudentRiskScoreFilter
    search_fields = ["enrollment__student__user__person__names"]
    ordering_fields = ["risk_score", "calculated_at", "risk_label"]
    ordering = ["-calculated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = StudentRiskScoreRepository()

    def get_queryset(self):
        """Obtiene el queryset, filtrando por DOCENTE si aplica."""
        qs = self.repository.get_all()
        user = self.request.user
        if user.is_authenticated and user.user_roles.filter(
            role__code="DOCENTE"
        ).exists():
            qs = qs.filter(
                enrollment__section__subject_offerings__teacher_assignments__user=user,
                enrollment__section__subject_offerings__teacher_assignments__is_active=True,
            ).distinct()
        return qs

    def perform_create(self, serializer):
        """Crea el puntaje a través del repositorio."""
        data = serializer.validated_data
        try:
            from ..application import validators

            errors = validators.run_all_validators(
                enrollment_id=data["enrollment"].id
                if hasattr(data["enrollment"], "id")
                else data["enrollment"],
                academic_period_id=data["academic_period"].id
                if hasattr(data["academic_period"], "id")
                else data["academic_period"],
                risk_score=data.get("risk_score"),
                risk_label=data.get("risk_label"),
            )
            if errors:
                raise ValueError(errors)

            score = StudentRiskScoreRepository.create(**data)
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = score

    def perform_update(self, serializer):
        """Actualiza el puntaje a través del repositorio."""
        data = dict(serializer.validated_data)
        try:
            score = StudentRiskScoreRepository.update(serializer.instance.id, **data)
        except ValueError as exc:
            _raise_validation_error(exc)
        serializer.instance = score

    @action(detail=False, methods=["post"])
    def calculate(self, request):
        """
        Inicia cálculo de riesgo para un estudiante (asíncrono).

        POST /api/analytics/student-risk-scores/calculate/
        Body: {"student_id": <id>, "academic_period_id": <id>}
        """
        student_id = request.data.get("student_id")
        academic_period_id = request.data.get("academic_period_id")

        if not student_id or not academic_period_id:
            return error_response(
                "student_id y academic_period_id son requeridos", status_code=400
            )

        try:
            task = StudentRiskCalculationService.calculate_risk(
                student_id, academic_period_id, user_id=request.user.id
            )
            return ok_response(
                {"task_id": task.id, "status": "PENDING"},
                msg="Cálculo de riesgo iniciado",
            )
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["post"])
    def batch_calculate(self, request):
        """
        Inicia cálculo de riesgo en batch (asíncrono).

        POST /api/analytics/student-risk-scores/batch_calculate/
        Body: {"academic_period_id": <id>, "student_ids": [<id>, ...]}
        """
        academic_period_id = request.data.get("academic_period_id")
        student_ids = request.data.get("student_ids")

        if not academic_period_id or not student_ids:
            return error_response(
                "academic_period_id y student_ids son requeridos", status_code=400
            )

        try:
            task = StudentRiskCalculationService.batch_calculate(
                academic_period_id, student_ids, user_id=request.user.id
            )
            return ok_response(
                {"task_id": task.id, "status": "PENDING"},
                msg="Cálculo de riesgo en batch iniciado",
            )
        except Exception as e:
            return error_response(str(e), status_code=400)

    @action(detail=False, methods=["post"])
    def simulate(self, request):
        """
        Evalúa el modelo/reglas con parámetros simulados (sin estudiante real).

        POST /api/analytics/student-risk-scores/simulate/
        Body: { attendance_rate, average_grade, failing_subjects_count,
                severe_incidents_count, mild_incidents_count, try_ml, ... }
        """
        serializer = SimulateRiskInputSerializer(data=request.data)
        if not serializer.is_valid():
            raise DRFValidationError(serializer.errors)

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

        config = RiskScoringConfigService.get_effective_config()
        config_serializer = RiskScoringConfigSerializer(config)

        rules_result = risk_engine.calculate_risk(snapshot, config=config)

        ml_result = None
        if params.get("try_ml") and config.engine == "ML":
            try:
                ml_score = risk_engine._predict_ml_score(snapshot)
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


# ─────────────────────────────────────────────────────────────────────────────
# RiskScoringConfig ViewSet
# ─────────────────────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        summary="Obtener configuración del motor de riesgo", tags=["analytics"]
    ),
    update_config=extend_schema(
        summary="Actualizar configuración del motor de riesgo", tags=["analytics"]
    ),
    apply_preset=extend_schema(
        summary="Aplicar preset de configuración", tags=["analytics"]
    ),
)
class RiskScoringConfigViewSet(BaseAnalyticsViewSet):
    """
    ViewSet para configuración GLOBAL (singleton) del motor de riesgo.

    - GET: Obtiene configuración actual (crea con defaults si no existe)
    - PATCH /update_config/: Actualiza campos específicos
    - POST /apply_preset/: Aplica un preset predefinido
    """

    serializer_class = RiskScoringConfigSerializer
    action_permissions = SCORING_CONFIG_ACTION_PERMISSIONS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = RiskScoringConfigRepository()

    def get_queryset(self):
        """Singleton: retorna lista con un solo elemento o vacía."""
        config = self.repository.get_singleton()
        if config:
            return [config]
        return []

    def get_object(self):
        """Retorna el singleton."""
        return self.repository.get_or_create_singleton()

    def list(self, request, *args, **kwargs):
        """GET /scoring-config/ - Retorna configuración actual."""
        config = self.repository.get_or_create_singleton()
        serializer = self.get_serializer(config)
        return ok_response(serializer.data)

    # Deshabilitar operaciones CRUD estándar
    def create(self, request, *args, **kwargs):
        return error_response("Use update_config para modificar la configuración", status_code=405)

    def update(self, request, *args, **kwargs):
        return error_response("Use PATCH /update_config/ para modificar", status_code=405)

    def destroy(self, request, *args, **kwargs):
        return error_response("La configuración no puede eliminarse", status_code=405)

    @action(detail=False, methods=["patch"])
    def update_config(self, request):
        """
        Actualiza campos específicos de la configuración.

        PATCH /api/analytics/scoring-config/update_config/
        Body: Campos a actualizar (partial update)
        """
        config = self.repository.get_or_create_singleton()
        serializer = RiskScoringConfigSerializer(
            config, data=request.data, partial=True
        )
        if not serializer.is_valid():
            raise DRFValidationError(serializer.errors)

        try:
            config = RiskScoringConfigService.update_config(**serializer.validated_data)
            return ok_response(
                RiskScoringConfigSerializer(config).data,
                msg="Configuración actualizada",
            )
        except ValueError as exc:
            _raise_validation_error(exc)

    @action(detail=False, methods=["post"])
    def apply_preset(self, request):
        """
        Aplica un preset predefinido a la configuración.

        POST /api/analytics/scoring-config/apply_preset/
        Body: {"preset": "conservador" | "equilibrado" | "estricto"}
        """
        preset_serializer = ApplyPresetSerializer(data=request.data)
        if not preset_serializer.is_valid():
            raise DRFValidationError(preset_serializer.errors)

        preset = preset_serializer.validated_data["preset"]

        try:
            config = RiskScoringConfigService.apply_preset(preset)
            return ok_response(
                RiskScoringConfigSerializer(config).data,
                msg=f"Preset '{preset}' aplicado",
            )
        except ValueError as exc:
            _raise_validation_error(exc)
