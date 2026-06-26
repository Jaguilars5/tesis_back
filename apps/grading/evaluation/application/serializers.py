from rest_framework import serializers

from ..infrastructure.models import EvaluationBlock, BlockComponent, EvaluativeActivity


class EvaluationBlockSerializer(serializers.ModelSerializer):
    academic_period_name = serializers.CharField(read_only=True)
    subject_offering_name = serializers.CharField(read_only=True)

    class Meta:
        model = EvaluationBlock
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class BlockComponentSerializer(serializers.ModelSerializer):
    evaluation_block_name = serializers.CharField(read_only=True)

    class Meta:
        model = BlockComponent
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class EvaluativeActivitySerializer(serializers.ModelSerializer):
    block_component_name = serializers.CharField(read_only=True)
    teacher_subject_section_name = serializers.CharField(read_only=True)
    subject_offering_name = serializers.CharField(read_only=True)
    activity_type_name = serializers.CharField(read_only=True, allow_null=True)

    class Meta:
        model = EvaluativeActivity
        fields = "__all__"
        read_only_fields = ["uuid", "created_at", "updated_at", "sync_version", "sync_status", "synced_at"]
