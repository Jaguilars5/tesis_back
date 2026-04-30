"""
Serializers de DRF para el módulo Analytics.
"""

from rest_framework import serializers
from ..models import StudentRiskScore, StudentFeatureSnapshot


class StudentRiskScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentRiskScore
        fields = "__all__"


class StudentFeatureSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeatureSnapshot
        fields = "__all__"
