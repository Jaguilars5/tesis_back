"""
Serializers de DRF para alertas tempranas.

Siguiendo el patrón academic_period: thin ModelSerializer con campos readonly
para desnormalización de relaciones.
"""

from rest_framework import serializers

from ..infrastructure.models import EarlyAlert, AlertTypeChoices, UrgencyLevelChoices


class EarlyAlertSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(read_only=True)
    academic_period_name = serializers.CharField(read_only=True)
    attended_by_user_name = serializers.CharField(read_only=True)

    class Meta:
        model = EarlyAlert
        fields = [
            "id",
            "enrollment",
            "enrollment_name",
            "academic_period",
            "academic_period_name",
            "alert_type",
            "description",
            "urgency_level",
            "attended",
            "attended_by_user",
            "attended_by_user_name",
            "detected_at",
            "attended_at",
            "response_actions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "enrollment",
            "academic_period",
            "alert_type",
            "description",
            "urgency_level",
            "detected_at",
            "attended_at",
            "created_at",
            "updated_at",
        ]
