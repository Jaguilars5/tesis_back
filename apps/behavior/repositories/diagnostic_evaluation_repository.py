from apps.core.repositories.base import BaseRepository
from apps.behavior.models import DiagnosticEvaluation


class DiagnosticEvaluationRepository(BaseRepository):
    model = DiagnosticEvaluation
