from rest_framework import serializers
from ...models import Parish


class ParishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parish
        fields = "__all__"
