"""
Serializers de DRF para el módulo Analytics.
"""

from decimal import Decimal

from rest_framework import serializers
from ..models import (
    RiskFactor,
    RiskScoringConfig,
    StudentFeatureSnapshot,
    StudentRiskFactor,
    StudentRiskScore,
)

# Rangos seguros (Auditoría §9.4): pesos acotados y dominios válidos.
WEIGHT_MIN = Decimal("10")
WEIGHT_MAX = Decimal("60")
WEIGHT_SUM = Decimal("100")
WEIGHT_SUM_TOLERANCE = Decimal("0.01")


class StudentRiskFactorSerializer(serializers.ModelSerializer):
    risk_factor_name = serializers.CharField(source="risk_factor.name", read_only=True)

    class Meta:
        model = StudentRiskFactor
        fields = "__all__"


class StudentRiskScoreSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(source="enrollment.__str__", read_only=True)
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )
    risk_factors = StudentRiskFactorSerializer(many=True, read_only=True)

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
        ]


class StudentFeatureSnapshotSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(source="enrollment.__str__", read_only=True)
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )

    class Meta:
        model = StudentFeatureSnapshot
        fields = "__all__"


class RiskFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskFactor
        fields = "__all__"


class RiskScoringConfigSerializer(serializers.ModelSerializer):
    """
    Serializer del singleton de configuración del motor de riesgo (Fase 5).

    Aplica los "parámetros seguros" (Auditoría §9.4): pesos suman 100% y están
    acotados, umbrales coherentes (rojo < amarillo) y dominios válidos
    (asistencia 0–100, notas 0–10).
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
            "average_red_max",
            "average_yellow_max",
            "severe_red_min",
            "mild_yellow_min",
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
        for field in ("attendance_red_max", "attendance_yellow_max"):
            value = Decimal(str(self._merged(attrs, field)))
            if value < 0 or value > 100:
                raise serializers.ValidationError({
                    field: "La asistencia debe estar entre 0 y 100.",
                })
        for field in ("average_red_max", "average_yellow_max"):
            value = Decimal(str(self._merged(attrs, field)))
            if value < 0 or value > 10:
                raise serializers.ValidationError({
                    field: "El promedio debe estar entre 0 y 10.",
                })
        for field in ("severe_red_min", "mild_yellow_min"):
            value = int(self._merged(attrs, field))
            if value < 0:
                raise serializers.ValidationError({
                    field: "El umbral no puede ser negativo.",
                })

    def _validate_threshold_coherence(self, attrs):
        attendance_red = Decimal(str(self._merged(attrs, "attendance_red_max")))
        attendance_yellow = Decimal(str(self._merged(attrs, "attendance_yellow_max")))
        if attendance_red >= attendance_yellow:
            raise serializers.ValidationError({
                "attendance_red_max": (
                    "El corte de asistencia para rojo debe ser menor al de amarillo "
                    "(rojo < amarillo < verde)."
                ),
            })
        average_red = Decimal(str(self._merged(attrs, "average_red_max")))
        average_yellow = Decimal(str(self._merged(attrs, "average_yellow_max")))
        if average_red >= average_yellow:
            raise serializers.ValidationError({
                "average_red_max": (
                    "El corte de promedio para rojo debe ser menor al de amarillo "
                    "(rojo < amarillo < verde)."
                ),
            })

    def validate(self, attrs):
        self._validate_weight_bounds(attrs)
        self._validate_weight_sum(attrs)
        self._validate_domains(attrs)
        self._validate_threshold_coherence(attrs)
        return attrs


class SimulateRiskInputSerializer(serializers.Serializer):
    attendance_rate = serializers.FloatField(min_value=0, max_value=100)
    average_grade = serializers.FloatField(min_value=0, max_value=10)
    failing_subjects_count = serializers.IntegerField(min_value=0)
    severe_incidents_count = serializers.IntegerField(min_value=0)
    mild_incidents_count = serializers.IntegerField(min_value=0)
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
    try_ml = serializers.BooleanField(default=False)



