from rest_framework import serializers

from ..infrastructure.models import AttendanceStatus


class AttendanceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceStatus
        fields = "__all__"
