from rest_framework import serializers
from ...models import SyncOperation, SyncStatus


class SyncOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncOperation
        fields = "__all__"


class SyncStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncStatus
        fields = "__all__"
