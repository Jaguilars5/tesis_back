from rest_framework import serializers

from ..infrastructure.models import QualitativeScale


class QualitativeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualitativeScale
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
