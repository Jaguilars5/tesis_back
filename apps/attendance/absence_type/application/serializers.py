from rest_framework import serializers

from ..infrastructure.models import AbsenceType


class AbsenceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsenceType
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
