from apps.core.repositories.base import BaseRepository

from ..domain.repositories import SubjectOfferingRepositoryInterface
from .models import SubjectOffering


class SubjectOfferingRepository(BaseRepository, SubjectOfferingRepositoryInterface):
    model = SubjectOffering

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.order_by("-id")

    @classmethod
    def get_by_section(cls, section_id, school_year_id=None):
        qs = cls.model.objects.filter(section_id=section_id).select_related(
            "section__school_year",
            "subject_academic_config__subject",
            "subject_academic_config__academic_grade",
        )
        if school_year_id:
            qs = qs.filter(section__school_year_id=school_year_id)
        return qs

    @classmethod
    def get_by_school_year(cls, school_year_id):
        return cls.model.objects.filter(
            section__school_year_id=school_year_id
        ).select_related(
            "section", "subject_academic_config__subject"
        )
