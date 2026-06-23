from rest_framework import serializers
from ...models import SpecialNeedsType


class SpecialNeedsTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialNeedsType
        fields = "__all__"
