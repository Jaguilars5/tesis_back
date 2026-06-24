from rest_framework import serializers

from ..infrastructure.models import PeriodType


class PeriodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodType
        fields = [
            "id",
            "code",
            "name",
            "description",
            "divisions_per_year",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
