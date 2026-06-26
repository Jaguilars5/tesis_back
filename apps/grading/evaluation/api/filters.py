from django_filters import rest_framework as filters

from ..infrastructure.models import EvaluationBlock, BlockComponent, EvaluativeActivity


class EvaluationBlockFilter(filters.FilterSet):
    academic_period = filters.NumberFilter(field_name="academic_period_id")
    subject_offering = filters.NumberFilter(field_name="subject_offering_id")
    is_active = filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = EvaluationBlock
        fields = ["academic_period", "subject_offering", "block_type", "is_active"]


class EvaluativeActivityFilter(filters.FilterSet):
    teacher_subject_section = filters.NumberFilter(
        field_name="teacher_subject_section_id"
    )
    academic_period = filters.NumberFilter(
        field_name="block_component__evaluation_block__academic_period_id"
    )

    class Meta:
        model = EvaluativeActivity
        fields = ["teacher_subject_section", "academic_period"]


class BlockComponentFilter(filters.FilterSet):
    evaluation_block = filters.NumberFilter(field_name="evaluation_block_id")
    subject_offering = filters.NumberFilter(
        field_name="evaluation_block__subject_offering_id"
    )
    academic_period = filters.NumberFilter(
        field_name="evaluation_block__academic_period_id"
    )
    is_active = filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = BlockComponent
        fields = ["evaluation_block", "subject_offering", "academic_period", "is_active"]
