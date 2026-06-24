from rest_framework import serializers

from ..infrastructure.models import EvaluationBlock, BlockComponent, EvaluativeActivity


class EvaluationBlockSerializer(serializers.ModelSerializer):
    academic_period_name = serializers.CharField(
        source="academic_period.name", read_only=True
    )

    class Meta:
        model = EvaluationBlock
        fields = "__all__"


class BlockComponentSerializer(serializers.ModelSerializer):
    evaluation_block_name = serializers.CharField(
        source="evaluation_block.name", read_only=True
    )

    class Meta:
        model = BlockComponent
        fields = "__all__"


class EvaluativeActivitySerializer(serializers.ModelSerializer):
    block_component_name = serializers.CharField(
        source="block_component.name", read_only=True
    )
    teacher_subject_section_name = serializers.CharField(
        source="teacher_subject_section.__str__", read_only=True
    )
    subject_offering_name = serializers.CharField(
        source="teacher_subject_section.subject_offering.__str__", read_only=True
    )
    activity_type_name = serializers.CharField(
        source="activity_type.name", read_only=True, allow_null=True
    )

    class Meta:
        model = EvaluativeActivity
        fields = "__all__"
        read_only_fields = ["uuid", "created_at", "updated_at", "sync_version", "sync_status", "synced_at"]
