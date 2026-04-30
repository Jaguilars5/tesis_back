"""
AnalyticsService - Lógica de procesamiento de datos y generación de riesgo.
"""

from ..repositories import (
    StudentRiskScoreRepository,
    StudentFeatureSnapshotRepository,
)


class AnalyticsService:
    """
    Servicio para gestionar los cálculos de riesgo y snapshots de métricas.
    """

    @staticmethod
    def get_student_risk_profile(student_id):
        """
        Retorna el perfil de riesgo completo de un estudiante, incluyendo el score
        más reciente y su último snapshot de métricas.
        """
        risk = StudentRiskScoreRepository.get_latest_by_student(student_id)
        snapshot = None
        if risk:
            snapshot = StudentFeatureSnapshotRepository.get_by_student_period(
                student_id, risk.academic_period_id
            )

        return {"risk_score": risk, "metrics_snapshot": snapshot}

    @staticmethod
    def list_priority_students(academic_period_id):
        """
        Retorna la lista de estudiantes con mayor riesgo en un periodo determinado.
        """
        return StudentRiskScoreRepository.list_high_risk(academic_period_id)
