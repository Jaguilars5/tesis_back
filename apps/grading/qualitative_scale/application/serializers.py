from rest_framework import serializers

from ..infrastructure.models import QualitativeScale, QualitativeScaleSublevel


class QualitativeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualitativeScale
        fields = "__all__"


class QualitativeScaleSublevelSerializer(serializers.ModelSerializer):
    scale_name = serializers.CharField(source="scale.name", read_only=True)
    sublevel_name = serializers.CharField(source="sublevel.name", read_only=True)

    class Meta:
        model = QualitativeScaleSublevel
        fields = "__all__"
