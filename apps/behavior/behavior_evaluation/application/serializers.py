from rest_framework import serializers

from ..infrastructure.models import BehaviorEvaluation


class BehaviorEvaluationSerializer(serializers.ModelSerializer):
    enrollment_name = serializers.CharField(read_only=True)
    academic_period_name = serializers.CharField(read_only=True)
    calculated_scale_name = serializers.CharField(read_only=True)
    final_scale_name = serializers.CharField(read_only=True)

    class Meta:
        model = BehaviorEvaluation
        fields = "__all__"
        read_only_fields = ["uuid", "created_at", "updated_at", "sync_version", "sync_status", "synced_at"]
