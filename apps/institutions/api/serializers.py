from rest_framework import serializers

from ..models import (
    AcademicGrade,
    AcademicLevel,
    AcademicSublevel,
    SchoolYear,
    Section,
)


class SchoolYearSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)

    class Meta:
        model = SchoolYear
        fields = ["id", "name", "start_date", "end_date", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "name", "created_at", "updated_at"]


class SectionSerializer(serializers.ModelSerializer):
    school_year_name = serializers.CharField(source="school_year.__str__", read_only=True)
    academic_grade_name = serializers.CharField(
        source="academic_grade.name", read_only=True
    )

    class Meta:
        model = Section
        fields = "__all__"


class AcademicLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicLevel
        fields = "__all__"


class AcademicSublevelSerializer(serializers.ModelSerializer):
    academic_level_name = serializers.CharField(
        source="academic_level.name", read_only=True
    )

    class Meta:
        model = AcademicSublevel
        fields = "__all__"


class AcademicGradeSerializer(serializers.ModelSerializer):
    academic_sublevel_name = serializers.CharField(
        source="academic_sublevel.name", read_only=True
    )

    class Meta:
        model = AcademicGrade
        fields = "__all__"
