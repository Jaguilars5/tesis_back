from rest_framework import serializers

from ..infrastructure.models import AcademicGrade


class AcademicGradeSerializer(serializers.ModelSerializer):
    academic_sublevel_name = serializers.CharField(
        source="academic_sublevel.name", read_only=True, allow_null=True
    )

    class Meta:
        model = AcademicGrade
        fields = [
            "id",
            "academic_sublevel",
            "academic_sublevel_name",
            "code",
            "name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
