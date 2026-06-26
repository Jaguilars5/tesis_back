from rest_framework import serializers

from ..infrastructure.models import SyncQueue


class SyncQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncQueue
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
