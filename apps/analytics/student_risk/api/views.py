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
from .filters import (
    StudentRiskScoreFilter,
    StudentRiskFactorFilter,
    StudentFeatureSnapshotFilter,
)
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
    # Catálogo de referencia gestionado por el sistema: solo lectura.
    http_method_names = ["get", "head", "options"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = RiskFactorRepository()

    def get_queryset(self):
        return self.repository.get_all()


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
    filterset_class = StudentRiskFactorFilter
    ordering_fields = ["contribution_weight", "created_at"]
    ordering = ["-contribution_weight"]
    # Derivado del cálculo de riesgo (A4): solo lectura.
    http_method_names = ["get", "head", "options"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = StudentRiskFactorRepository()

    def get_queryset(self):
        return self.repository.get_all()


# ─────────────────────────────────────────────────────────────────────────────
# StudentFeatureSnapshot ViewSet
# ─────────────────────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(summary="Listar snapshots de features", tags=["analytics"]),
    get=extend_schema(summary="Obtener snapshot de features", tags=["analytics"]),
)
class StudentFeatureSnapshotViewSet(BaseAnalyticsViewSet):
    """ViewSet para snapshots de features de estudiantes."""

    serializer_class = StudentFeatureSnapshotSerializer
    action_permissions = FEATURE_SNAPSHOT_ACTION_PERMISSIONS
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentFeatureSnapshotFilter
    search_fields = ["enrollment__student__user__person__names"]
    ordering_fields = [
        "calculated_at",
        "risk_score",
        "attendance_rate",
        "failing_subjects_count",
    ]
    ordering = ["-calculated_at"]
    # Snapshots calculados (A4): se generan automáticamente, solo lectura.
    http_method_names = ["get", "head", "options"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = StudentFeatureSnapshotRepository()

    def get_queryset(self):
        return self.repository.get_all()


# ─────────────────────────────────────────────────────────────────────────────
# StudentRiskScore ViewSet
# ─────────────────────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(summary="Listar puntajes de riesgo", tags=["analytics"]),
    get=extend_schema(summary="Obtener puntaje de riesgo", tags=["analytics"]),
    create=extend_schema(exclude=True),
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
    filterset_class = StudentRiskScoreFilter
    search_fields = ["enrollment__student__user__person__names"]
    ordering_fields = ["risk_score", "calculated_at", "risk_label"]
    ordering = ["-calculated_at"]
    # Calculado (A4): se genera vía calculate/batch_calculate. Sin PUT/PATCH/DELETE.
    http_method_names = ["get", "post", "head", "options"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = StudentRiskScoreRepository()

    def get_queryset(self):
        """Obtiene el queryset, filtrando por DOCENTE si aplica."""
        return self.repository.get_visible_for_user(self.request.user)

    # El POST de colección no crea recursos: el riesgo se calcula de forma async.
    def create(self, request, *args, **kwargs):
        return error_response(
            "Los puntajes de riesgo se generan automáticamente. "
            "Use /calculate/ o /batch_calculate/",
            status_code=405,
        )

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

        result = StudentRiskCalculationService.simulate(serializer.validated_data)

        return ok_response({
            "reglas": result["reglas"],
            "ml": result["ml"],
            "produccion": result["produccion"],
            "config_usada": result["config_simulacion"],
            "config_institucional": result["config_institucional"],
        })

    @extend_schema(
        summary="Predecir riesgo por materia",
        description="Usa el modelo ML por materia para predecir si una materia espec\u00edfica se ir\u00e1 a rojo",
        tags=["analytics"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "enrollment_id": {"type": "integer"},
                    "subject_code": {"type": "string"},
                    "academic_period_id": {"type": "integer"},
                },
                "required": ["enrollment_id", "subject_code", "academic_period_id"],
            }
        },
        responses={200: {"type": "object"}},
    )
    @action(detail=False, methods=["post"])
    def predict_subject_risk(self, request):
        enrollment_id = request.data.get("enrollment_id")
        subject_code = request.data.get("subject_code")
        academic_period_id = request.data.get("academic_period_id")

        if not all([enrollment_id, subject_code, academic_period_id]):
            return error_response(
                "enrollment_id, subject_code y academic_period_id son requeridos",
                status_code=400,
            )

        try:
            enrollment_id = int(enrollment_id)
            academic_period_id = int(academic_period_id)
            subject_code = subject_code.upper()
        except (TypeError, ValueError):
            return error_response("Par\u00e1metros inv\u00e1lidos", status_code=400)

        from apps.analytics.ml.subject_model import SubjectRiskModelTrainer

        result = SubjectRiskModelTrainer.predict(
            enrollment_id, subject_code, academic_period_id
        )

        if result is None:
            return ok_response(
                {
                    "subject_code": subject_code,
                    "probability": None,
                    "risk_level": "desconocido",
                    "error": "No hay datos suficientes o modelo no entrenado",
                },
                msg="No se pudo calcular riesgo para esta materia",
            )

        return ok_response(result)

    @extend_schema(
        summary="Predecir riesgo anual",
        description="Usa el modelo ML anual para predecir si el estudiante perder\u00e1 el a\u00f1o",
        tags=["analytics"],
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
        responses={200: {"type": "object"}},
    )
    @action(detail=False, methods=["post"])
    def predict_annual_risk(self, request):
        enrollment_id = request.data.get("enrollment_id")
        academic_period_id = request.data.get("academic_period_id")

        if not all([enrollment_id, academic_period_id]):
            return error_response(
                "enrollment_id y academic_period_id son requeridos",
                status_code=400,
            )

        try:
            enrollment_id = int(enrollment_id)
            academic_period_id = int(academic_period_id)
        except (TypeError, ValueError):
            return error_response("Par\u00e1metros inv\u00e1lidos", status_code=400)

        from apps.analytics.ml.annual_model import AnnualRiskModelTrainer

        result = AnnualRiskModelTrainer.predict(enrollment_id, academic_period_id)

        if result is None:
            return ok_response(
                {
                    "probability": None,
                    "risk_level": "desconocido",
                    "error": "No hay snapshot o modelo no entrenado",
                },
                msg="No se pudo calcular riesgo anual",
            )

        return ok_response(result)


# ─────────────────────────────────────────────────────────────────────────────
# RiskScoringConfig ViewSet
# ─────────────────────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        summary="Obtener configuración del motor de riesgo", tags=["analytics"]
    ),
    create=extend_schema(exclude=True),
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
    # Singleton de configuración: lectura + acciones (update_config / apply_preset).
    http_method_names = ["get", "post", "patch", "head", "options"]

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

    # El POST de colección no crea recursos (singleton). Usar update_config/apply_preset.
    def create(self, request, *args, **kwargs):
        return error_response(
            "Use update_config o apply_preset para modificar la configuración",
            status_code=405,
        )

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
