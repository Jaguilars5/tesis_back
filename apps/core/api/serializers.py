from rest_framework import serializers
from apps.core.models import SyncQueue


class SyncQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncQueue
        fields = "__all__"
