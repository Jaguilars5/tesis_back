from rest_framework import serializers

from ..infrastructure.models import AcademicSublevel


class AcademicSublevelSerializer(serializers.ModelSerializer):
    academic_level_name = serializers.CharField(
        source="academic_level.name", read_only=True
    )

    class Meta:
        model = AcademicSublevel
        fields = "__all__"
