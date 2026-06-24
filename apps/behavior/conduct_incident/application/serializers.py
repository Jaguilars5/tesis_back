from rest_framework import serializers

from ..infrastructure.models import ConductIncident


class ConductIncidentSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(source="enrollment.__str__", read_only=True)
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )
    incident_type_name = serializers.CharField(
        source="incident_type.name", read_only=True
    )
    severity_name = serializers.CharField(source="severity.name", read_only=True)

    class Meta:
        model = ConductIncident
        fields = "__all__"
        read_only_fields = ["uuid", "created_at", "updated_at", "sync_version", "sync_status", "synced_at"]
