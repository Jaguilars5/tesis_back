from rest_framework import serializers
from ..models import (
    AcademicGrade,
    AcademicLevel,
    Classroom,
    DocumentType,
    RoomType,
    School_Year,
)


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


class AcademicLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicLevel
        fields = "__all__"


class AcademicGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicGrade
        fields = "__all__"
