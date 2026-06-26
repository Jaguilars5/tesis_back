from rest_framework import serializers

from ..infrastructure.models import AttendanceStatus


class AttendanceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceStatus
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
