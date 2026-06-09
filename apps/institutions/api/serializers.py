from rest_framework import serializers

from ..models import (
    AcademicGrade,
    AcademicLevel,
    AcademicSublevel,
    SchoolYear,
    Section,
)


class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYear
        fields = "__all__"


class SectionSerializer(serializers.ModelSerializer):
    school_year_name = serializers.CharField(source="school_year.name", read_only=True)
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
    academic_level_name = serializers.CharField(
        source="academic_level.name", read_only=True
    )

    class Meta:
        model = AcademicGrade
        fields = "__all__"
