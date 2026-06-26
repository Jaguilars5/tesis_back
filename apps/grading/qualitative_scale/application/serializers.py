from rest_framework import serializers

from ..infrastructure.models import QualitativeScale, QualitativeScaleSublevel


class QualitativeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualitativeScale
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class QualitativeScaleSublevelSerializer(serializers.ModelSerializer):
    scale_name = serializers.CharField(read_only=True)
    sublevel_name = serializers.CharField(read_only=True)

    class Meta:
        model = QualitativeScaleSublevel
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
