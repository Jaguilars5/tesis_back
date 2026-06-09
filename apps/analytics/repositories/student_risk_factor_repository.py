from apps.core.repositories.base import BaseRepository
from ..models import StudentRiskFactor


class StudentRiskFactorRepository(BaseRepository):
    model = StudentRiskFactor

    @classmethod
    def get_all(cls, active_only=True):
        queryset = super().get_all(active_only=active_only)
        return queryset.select_related("student_risk_score", "risk_factor").order_by("-id")
