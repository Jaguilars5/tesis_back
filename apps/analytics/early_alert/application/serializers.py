"""
Serializers de DRF para alertas tempranas.

Siguiendo el patrón academic_period: thin ModelSerializer con campos readonly
para desnormalización de relaciones.
"""

from rest_framework import serializers

from ..infrastructure.models import EarlyAlert, AlertTypeChoices, UrgencyLevelChoices


class EarlyAlertSerializer(serializers.ModelSerializer):
    """
    Serializer para EarlyAlert.

    Campos readonly para relaciones:
    - enrollment_name: representación de la matrícula
    - academic_period_name: nombre del período académico
    - attended_by_user_name: nombre del usuario que atendió
    """

    enrollment_name = serializers.CharField(
        source="enrollment.__str__", read_only=True
    )
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )
    attended_by_user_name = serializers.CharField(
        source="attended_by_user.person.get_full_name", read_only=True
    )

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
            "is_active",
        ]
        read_only_fields = [
            "id",
            "detected_at",
            "attended_at",
            "created_at",
            "updated_at",
        ]


class EarlyAlertCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para creación de alertas tempranas.

    Versión más estricta que valida campos requeridos.
    """

    class Meta:
        model = EarlyAlert
        fields = [
            "enrollment",
            "academic_period",
            "alert_type",
            "description",
            "urgency_level",
        ]

    def validate_description(self, value):
        """La descripción no puede estar vacía."""
        if not value or not value.strip():
            raise serializers.ValidationError("La descripción es requerida.")
        return value
