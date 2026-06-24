from apps.core.repositories.base import BaseRepository

from .models import EvaluationBlock, BlockComponent, EvaluativeActivity


class EvaluationBlockRepository(BaseRepository):
    model = EvaluationBlock

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("academic_period")


class BlockComponentRepository(BaseRepository):
    model = BlockComponent

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("evaluation_block")


class EvaluativeActivityRepository(BaseRepository):
    model = EvaluativeActivity

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("block_component", "teacher_subject_section", "activity_type")
