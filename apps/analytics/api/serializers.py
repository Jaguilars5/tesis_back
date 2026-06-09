"""
Serializers de DRF para el módulo Analytics.
"""

from rest_framework import serializers
from ..models import (
    AlertType,
    EarlyAlert,
    RiskFactor,
    StudentFeatureSnapshot,
    StudentRiskFactor,
    StudentRiskScore,
    UrgencyLevel,
)


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


class AlertTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertType
        fields = "__all__"


class UrgencyLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrgencyLevel
        fields = "__all__"


class RiskFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskFactor
        fields = "__all__"


class EarlyAlertSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(source="enrollment.__str__", read_only=True)
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )
    attended_by_user_name = serializers.CharField(
        source="attended_by_user.person.get_full_name", read_only=True
    )

    class Meta:
        model = EarlyAlert
        fields = "__all__"
