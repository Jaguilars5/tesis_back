from rest_framework import serializers

from ..infrastructure.models import Section


class SectionSerializer(serializers.ModelSerializer):
    school_year_name = serializers.CharField(source="school_year.__str__", read_only=True)
    academic_grade_name = serializers.CharField(
        source="academic_grade.name", read_only=True
    )

    class Meta:
        model = Section
        fields = "__all__"
