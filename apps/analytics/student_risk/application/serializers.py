"""
Serializers de DRF para riesgo estudiantil.
"""

from decimal import Decimal
from rest_framework import serializers

from ..infrastructure.models import (
    RiskFactor,
    StudentRiskScore,
    StudentRiskFactor,
    StudentFeatureSnapshot,
    RiskScoringConfig,
    ScoringEngineChoices,
    ScoringPresetChoices,
)


# ─────────────────────────────────────────────────────────────────────────────
# RiskFactor Serializers
# ─────────────────────────────────────────────────────────────────────────────

class RiskFactorSerializer(serializers.ModelSerializer):
    """Serializer para catálogo de factores de riesgo."""

    class Meta:
        model = RiskFactor
        fields = ["id", "code", "name", "description", "created_at", "updated_at"]


# ─────────────────────────────────────────────────────────────────────────────
# StudentRiskFactor Serializers
# ─────────────────────────────────────────────────────────────────────────────

class StudentRiskFactorSerializer(serializers.ModelSerializer):
    """Serializer para factores de riesgo por estudiante."""

    risk_factor_name = serializers.CharField(
        source="risk_factor.name", read_only=True
    )

    class Meta:
        model = StudentRiskFactor
        fields = [
            "id",
            "student_risk_score",
            "risk_factor",
            "risk_factor_name",
            "contribution_weight",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


# ─────────────────────────────────────────────────────────────────────────────
# StudentRiskScore Serializers
# ─────────────────────────────────────────────────────────────────────────────

class StudentRiskScoreSerializer(serializers.ModelSerializer):
    """
    Serializer para puntajes de riesgo.

    Campos readonly para desnormalización de relaciones.
    """

    enrollment_name = serializers.CharField(
        source="enrollment.__str__", read_only=True
    )
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )
    risk_factors = StudentRiskFactorSerializer(many=True, read_only=True)
    feature_importances = serializers.SerializerMethodField()

    class Meta:
        model = StudentRiskScore
        fields = [
            "id",
            "enrollment",
            "enrollment_name",
            "academic_period",
            "academic_period_name",
            "risk_score",
            "risk_label",
            "model_version",
            "calculated_at",
            "risk_factors",
            "feature_importances",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "calculated_at", "created_at", "updated_at"]

    def get_feature_importances(self, obj):
        """Retorna las feature importances del modelo ML si está activo."""
        try:
            from apps.analytics.ml.features import TRAIN_FEATURES
            from apps.analytics.student_risk.domain.risk_engine import (
                _load_artifact_cached,
            )

            if "sklearn" not in (obj.model_version or ""):
                return None

            artifact = _load_artifact_cached()
            if artifact is None:
                return None

            importances = artifact.get("feature_importances")
            if not importances or len(importances) != len(TRAIN_FEATURES):
                return None

            return [
                {
                    "feature": TRAIN_FEATURES[i],
                    "importance": round(float(importances[i]), 4),
                }
                for i in range(len(TRAIN_FEATURES))
                if float(importances[i]) > 0.001
            ]
        except Exception:
            return None

    def to_representation(self, instance):
        """La etiqueta siempre se deriva del puntaje (evita desincronización en BD)."""
        from apps.analytics.student_risk.domain.risk_engine import score_to_risk_label

        data = super().to_representation(instance)
        data["risk_label"] = score_to_risk_label(float(instance.risk_score))
        return data


# ─────────────────────────────────────────────────────────────────────────────
# StudentFeatureSnapshot Serializers
# ─────────────────────────────────────────────────────────────────────────────

class StudentFeatureSnapshotSerializer(serializers.ModelSerializer):
    """
    Serializer para snapshots de features.

    Campos readonly para desnormalización de relaciones.
    """

    enrollment_name = serializers.CharField(
        source="enrollment.__str__", read_only=True
    )
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )

    class Meta:
        model = StudentFeatureSnapshot
        fields = [
            "id",
            "enrollment",
            "enrollment_name",
            "academic_period",
            "academic_period_name",
            "attendance_rate",
            "consecutive_absences_max",
            "tardiness_count",
            "justified_absences",
            "unjustified_absences",
            "formative_avg_normalized",
            "summative_avg_normalized",
            "grade_trend_slope",
            "failing_subjects_count",
            "conduct_score",
            "severe_incidents_count",
            "family_notified_ratio",
            "prev_period_avg_grade",
            "age_grade_gap",
            "is_repeat",
            "has_special_needs",
            "city",
            "special_needs_type",
            "withdrawal_reason",
            "is_current",
            "snapshot_trigger",
            "calculated_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "calculated_at", "created_at", "updated_at"]


# ─────────────────────────────────────────────────────────────────────────────
# RiskScoringConfig Serializers
# ─────────────────────────────────────────────────────────────────────────────

# Rangos seguros (Auditoría §9.4)
WEIGHT_MIN = Decimal("10")
WEIGHT_MAX = Decimal("60")
WEIGHT_SUM = Decimal("100")
WEIGHT_SUM_TOLERANCE = Decimal("0.01")


class RiskScoringConfigSerializer(serializers.ModelSerializer):
    """
    Serializer para configuración del motor de riesgo.

    Aplica validaciones de parámetros seguros (Auditoría §9.4):
    - Pesos suman 100% y están acotados 10-60%
    - Umbrales coherentes (rojo < amarillo)
    - Dominios válidos (asistencia 0-100, notas 0-10)
    """

    class Meta:
        model = RiskScoringConfig
        fields = [
            "id",
            "engine",
            "preset",
            "weight_conducta",
            "weight_asistencia",
            "weight_calificaciones",
            "attendance_red_max",
            "attendance_yellow_max",
            "attendance_green_min",
            "average_red_max",
            "average_yellow_max",
            "average_green_min",
            "severe_red_min",
            "mild_yellow_min",
            "severe_green_max",
            "mild_green_max",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def _merged(self, attrs, field):
        """Valor entrante o, si no viene (PATCH parcial), el actual de la instancia."""
        if field in attrs:
            return attrs[field]
        if self.instance is not None:
            return getattr(self.instance, field)
        return self.fields[field].get_default()

    def _validate_weight_bounds(self, attrs):
        for field in ("weight_conducta", "weight_asistencia", "weight_calificaciones"):
            value = Decimal(str(self._merged(attrs, field)))
            if value < WEIGHT_MIN or value > WEIGHT_MAX:
                raise serializers.ValidationError({
                    field: f"El peso debe estar entre {WEIGHT_MIN}% y {WEIGHT_MAX}%.",
                })

    def _validate_weight_sum(self, attrs):
        total = sum(
            Decimal(str(self._merged(attrs, field)))
            for field in (
                "weight_conducta",
                "weight_asistencia",
                "weight_calificaciones",
            )
        )
        if abs(total - WEIGHT_SUM) > WEIGHT_SUM_TOLERANCE:
            raise serializers.ValidationError({
                "weights": f"Los pesos deben sumar 100% (suma actual: {total}%).",
            })

    def _validate_domains(self, attrs):
        for field in (
            "attendance_red_max",
            "attendance_yellow_max",
            "attendance_green_min",
        ):
            value = Decimal(str(self._merged(attrs, field)))
            if value < 0 or value > 100:
                raise serializers.ValidationError({
                    field: "La asistencia debe estar entre 0 y 100.",
                })
        for field in ("average_red_max", "average_yellow_max", "average_green_min"):
            value = Decimal(str(self._merged(attrs, field)))
            if value < 0 or value > 10:
                raise serializers.ValidationError({
                    field: "El promedio debe estar entre 0 y 10.",
                })
        for field in (
            "severe_red_min",
            "mild_yellow_min",
            "severe_green_max",
            "mild_green_max",
        ):
            value = int(self._merged(attrs, field))
            if value < 0:
                raise serializers.ValidationError({
                    field: "El umbral no puede ser negativo.",
                })

    def _validate_threshold_coherence(self, attrs):
        attendance_red = Decimal(str(self._merged(attrs, "attendance_red_max")))
        attendance_yellow = Decimal(str(self._merged(attrs, "attendance_yellow_max")))
        attendance_green = Decimal(str(self._merged(attrs, "attendance_green_min")))
        if attendance_red >= attendance_yellow:
            raise serializers.ValidationError({
                "attendance_red_max": (
                    "El corte rojo de asistencia debe ser menor al de amarillo "
                    "(rojo < amarillo < verde)."
                ),
            })
        if attendance_yellow >= attendance_green:
            raise serializers.ValidationError({
                "attendance_green_min": (
                    "El mínimo verde de asistencia debe ser mayor al tope amarillo "
                    "(rojo < amarillo < verde)."
                ),
            })
        average_red = Decimal(str(self._merged(attrs, "average_red_max")))
        average_yellow = Decimal(str(self._merged(attrs, "average_yellow_max")))
        average_green = Decimal(str(self._merged(attrs, "average_green_min")))
        if average_red >= average_yellow:
            raise serializers.ValidationError({
                "average_red_max": (
                    "El corte rojo de promedio debe ser menor al de amarillo "
                    "(rojo < amarillo < verde)."
                ),
            })
        if average_yellow >= average_green:
            raise serializers.ValidationError({
                "average_green_min": (
                    "El mínimo verde de promedio debe ser mayor al tope amarillo "
                    "(rojo < amarillo < verde)."
                ),
            })
        severe_red = int(self._merged(attrs, "severe_red_min"))
        severe_green = int(self._merged(attrs, "severe_green_max"))
        mild_yellow = int(self._merged(attrs, "mild_yellow_min"))
        mild_green = int(self._merged(attrs, "mild_green_max"))
        if severe_green > severe_red:
            raise serializers.ValidationError({
                "severe_green_max": (
                    "El máximo verde de faltas graves debe ser menor o igual al umbral rojo."
                ),
            })
        if mild_green > mild_yellow:
            raise serializers.ValidationError({
                "mild_green_max": (
                    "El máximo verde de faltas leves debe ser menor o igual al umbral amarillo."
                ),
            })

    def validate(self, attrs):
        self._validate_weight_bounds(attrs)
        self._validate_weight_sum(attrs)
        self._validate_domains(attrs)
        self._validate_threshold_coherence(attrs)
        return attrs


class SimulateConfigOverrideSerializer(serializers.Serializer):
    """Overrides opcionales del motor para el simulador (no persisten en BD)."""

    preset = serializers.ChoiceField(
        choices=["conservador", "equilibrado", "estricto", "personalizado"],
        required=False,
    )
    engine = serializers.ChoiceField(choices=["reglas", "ML"], required=False)
    weight_conducta = serializers.FloatField(min_value=10, max_value=60, required=False)
    weight_asistencia = serializers.FloatField(min_value=10, max_value=60, required=False)
    weight_calificaciones = serializers.FloatField(min_value=10, max_value=60, required=False)
    attendance_red_max = serializers.FloatField(min_value=0, max_value=100, required=False)
    attendance_yellow_max = serializers.FloatField(min_value=0, max_value=100, required=False)
    average_red_max = serializers.FloatField(min_value=0, max_value=10, required=False)
    average_yellow_max = serializers.FloatField(min_value=0, max_value=10, required=False)
    severe_red_min = serializers.IntegerField(min_value=0, required=False)
    mild_yellow_min = serializers.IntegerField(min_value=0, required=False)
    attendance_green_min = serializers.FloatField(min_value=0, max_value=100, required=False)
    average_green_min = serializers.FloatField(min_value=0, max_value=10, required=False)
    severe_green_max = serializers.IntegerField(min_value=0, required=False)
    mild_green_max = serializers.IntegerField(min_value=0, required=False)


class SimulateRiskInputSerializer(serializers.Serializer):
    attendance_rate = serializers.FloatField(min_value=0, max_value=100)
    average_grade = serializers.FloatField(min_value=0, max_value=10)
    failing_subjects_count = serializers.IntegerField(min_value=0)
    severe_incidents_count = serializers.IntegerField(min_value=0)
    mild_incidents_count = serializers.IntegerField(min_value=0)
    moderate_incidents_count = serializers.IntegerField(min_value=0, default=0)
    consecutive_absences_max = serializers.IntegerField(min_value=0, default=0)
    tardiness_count = serializers.IntegerField(min_value=0, default=0)
    justified_absences = serializers.IntegerField(min_value=0, default=0)
    unjustified_absences = serializers.IntegerField(min_value=0, default=0)
    grade_trend_slope = serializers.FloatField(default=0)
    family_notified_ratio = serializers.FloatField(min_value=0, max_value=1, default=0)
    prev_period_avg_grade = serializers.FloatField(default=0)
    age_grade_gap = serializers.IntegerField(min_value=0, default=0)
    is_repeat = serializers.BooleanField(default=False)
    has_special_needs = serializers.BooleanField(default=False)
    config_overrides = SimulateConfigOverrideSerializer(required=False)
    try_ml = serializers.BooleanField(default=True)


class ApplyPresetSerializer(serializers.Serializer):
    """Serializer para aplicar un preset de configuración."""

    preset = serializers.ChoiceField(choices=ScoringPresetChoices.choices)
