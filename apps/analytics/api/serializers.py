"""
Serializers de DRF para el módulo Analytics.
"""

from rest_framework import serializers
from ..models import RiskFactor, StudentFeatureSnapshot, StudentRiskFactor, StudentRiskScore


class StudentRiskFactorSerializer(serializers.ModelSerializer):
    risk_factor_name = serializers.CharField(source="risk_factor.name", read_only=True)

    class Meta:
        model = StudentRiskFactor
        fields = "__all__"


class StudentRiskScoreSerializer(serializers.ModelSerializer):
    risk_factors = StudentRiskFactorSerializer(many=True, read_only=True)

    class Meta:
        model = StudentRiskScore
        fields = ["id", "student", "academic_period", "risk_score", "risk_label",
                   "model_version", "calculated_at", "risk_factors"]


class StudentFeatureSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeatureSnapshot
        fields = "__all__"


class RiskFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskFactor
        fields = "__all__"
