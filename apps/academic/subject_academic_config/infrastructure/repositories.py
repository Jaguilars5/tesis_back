from apps.core.repositories.base import BaseRepository

from ..domain.repositories import SubjectAcademicConfigRepositoryInterface
from .models import SubjectAcademicConfig


class SubjectAcademicConfigRepository(BaseRepository, SubjectAcademicConfigRepositoryInterface):
    model = SubjectAcademicConfig

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_by_subject(cls, subject_id):
        return cls.model.objects.filter(subject_id=subject_id).select_related(
            "academic_grade", "subject"
        )

    @classmethod
    def get_by_grade(cls, academic_grade_id):
        return cls.model.objects.filter(
            academic_grade_id=academic_grade_id
        ).select_related("subject", "academic_grade")
