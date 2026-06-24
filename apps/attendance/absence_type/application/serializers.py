from rest_framework import serializers

from ..infrastructure.models import AbsenceType


class AbsenceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsenceType
        fields = "__all__"
