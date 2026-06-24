from rest_framework import serializers

from ..infrastructure.models import Severity


class SeveritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Severity
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
