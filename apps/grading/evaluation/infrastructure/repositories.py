from apps.core.repositories.base import BaseRepository

from ..domain.repositories import (
    EvaluationBlockRepositoryInterface,
    BlockComponentRepositoryInterface,
    EvaluativeActivityRepositoryInterface,
)
from .models import EvaluationBlock, BlockComponent, EvaluativeActivity


class EvaluationBlockRepository(BaseRepository, EvaluationBlockRepositoryInterface):
    model = EvaluationBlock

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("academic_period")

    @classmethod
    def get_blocks_for_period(cls, academic_period_id):
        return cls.model.objects.filter(
            academic_period_id=academic_period_id,
            is_active=True,
        )

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        child_ids = list(BlockComponent.objects.filter(
            evaluation_block_id=instance_id, is_active=True
        ).values_list("id", flat=True))
        counts = {}
        if child_ids:
            counts["componentes de bloque"] = len(child_ids)
        return counts

    @classmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        child_ids = list(BlockComponent.objects.filter(
            evaluation_block_id=instance_id, is_active=True
        ).values_list("id", flat=True))
        total = 0
        if child_ids:
            total += BlockComponent.objects.filter(id__in=child_ids).update(is_active=False)
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return total


class BlockComponentRepository(BaseRepository, BlockComponentRepositoryInterface):
    model = BlockComponent

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("evaluation_block")

    @classmethod
    def get_active_component_for_offering(cls, subject_offering_id):
        return cls.model.objects.filter(
            evaluation_block__subject_offering_id=subject_offering_id,
            is_active=True,
        ).select_related("evaluation_block").first()

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        child_ids = list(EvaluativeActivity.objects.filter(
            block_component_id=instance_id, is_active=True
        ).values_list("id", flat=True))
        counts = {}
        if child_ids:
            counts["actividades evaluativas"] = len(child_ids)
        return counts

    @classmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        child_ids = list(EvaluativeActivity.objects.filter(
            block_component_id=instance_id, is_active=True
        ).values_list("id", flat=True))
        total = 0
        if child_ids:
            total += EvaluativeActivity.objects.filter(id__in=child_ids).update(is_active=False)
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return total


class EvaluativeActivityRepository(BaseRepository, EvaluativeActivityRepositoryInterface):
    model = EvaluativeActivity

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("block_component", "teacher_subject_section", "activity_type")

    @classmethod
    def get_notes_for_block(cls, enrollment_id, evaluation_block_id):
        from apps.grading.student_note.infrastructure.models import StudentNote
        return list(StudentNote.objects.filter(
            enrollment_id=enrollment_id,
            evaluative_activity__block_component__evaluation_block_id=evaluation_block_id,
        ).select_related(
            "evaluative_activity__block_component__evaluation_block"
        ))

    @classmethod
    def get_cascade_counts(cls, instance_id: int) -> dict[str, int]:
        return {}

    @classmethod
    def deactivate_cascade(cls, instance_id: int) -> int:
        cls.model.objects.filter(pk=instance_id).update(is_active=False)
        return 1
