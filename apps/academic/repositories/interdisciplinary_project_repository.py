from apps.core.repositories.base import BaseRepository
from apps.academic.models import InterdisciplinaryProject, SubjectProject


class InterdisciplinaryProjectRepository(BaseRepository):
    model = InterdisciplinaryProject

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_active_by_period(cls, academic_period_id):
        return cls.model.objects.filter(
            academic_period_id=academic_period_id,
            is_active=True,
        ).prefetch_related("subject_projects__subject_offering")


class SubjectProjectRepository(BaseRepository):
    model = SubjectProject

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")
