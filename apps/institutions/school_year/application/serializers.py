from rest_framework import serializers

from ..infrastructure.models import SchoolYear


class SchoolYearSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)

    class Meta:
        model = SchoolYear
        fields = ["id", "name", "start_date", "end_date", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "name", "created_at", "updated_at"]
