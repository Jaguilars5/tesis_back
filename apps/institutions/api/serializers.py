from rest_framework import serializers
from ..models import (
    AcademicGrade,
    AcademicLevel,
    AcademicRegime,
    Classroom,
    DocumentType,
    Institution,
    RoomType,
    School_Year,
)


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = "__all__"


class School_YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = School_Year
        fields = "__all__"


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = "__all__"

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La capacidad debe ser mayor a 0")
        return value


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = "__all__"


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = "__all__"


class AcademicRegimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicRegime
        fields = "__all__"


class AcademicLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicLevel
        fields = "__all__"


class AcademicGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicGrade
        fields = "__all__"
