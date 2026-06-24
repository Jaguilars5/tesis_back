from rest_framework import serializers

from ..infrastructure.models import AcademicLevel


class AcademicLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicLevel
        fields = "__all__"
