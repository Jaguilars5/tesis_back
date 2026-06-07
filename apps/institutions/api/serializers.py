from rest_framework import serializers
from ..models import (
    AcademicGrade,
    AcademicLevel,
    DocumentType,
    School_Year,
    Section,
)


class School_YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = School_Year
        fields = "__all__"


class SectionSerializer(serializers.ModelSerializer):
    school_year_name = serializers.CharField(source="school_year.name", read_only=True)
    academic_grade_name = serializers.CharField(
        source="academic_grade.name", read_only=True
    )

    class Meta:
        model = Section
        fields = "__all__"


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = "__all__"


class AcademicLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicLevel
        fields = "__all__"


class AcademicGradeSerializer(serializers.ModelSerializer):
    academic_level_name = serializers.CharField(
        source="academic_level.name", read_only=True
    )

    class Meta:
        model = AcademicGrade
        fields = "__all__"
