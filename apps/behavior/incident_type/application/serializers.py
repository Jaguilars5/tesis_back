from rest_framework import serializers

from ..infrastructure.models import IncidentType


class IncidentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentType
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
