"""
Analytics repositories - Acceso a datos de riesgo y métricas.
"""

from ..models import StudentRiskScore, StudentFeatureSnapshot


class BaseRepository:
    model = None

    @classmethod
    def get_all(cls):
        return cls.model.objects.all()

    @classmethod
    def get_by_id(cls, pk):
        try:
            return cls.model.objects.get(pk=pk)
        except cls.model.DoesNotExist:
            return None


class StudentRiskScoreRepository(BaseRepository):
    model = StudentRiskScore

    @classmethod
    def get_latest_by_student(cls, student_id):
        """Obtiene el puntaje de riesgo más reciente de un estudiante."""
        return cls.model.objects.filter(student_id=student_id).first()

    @classmethod
    def list_high_risk(cls, academic_period_id, threshold=70):
        """Lista estudiantes con riesgo alto según un umbral."""
        return cls.model.objects.filter(
            academic_period_id=academic_period_id, risk_score__gte=threshold
        ).select_related("student")


class StudentFeatureSnapshotRepository(BaseRepository):
    model = StudentFeatureSnapshot

    @classmethod
    def get_by_student_period(cls, student_id, academic_period_id):
        """Obtiene la foto de métricas para un estudiante y periodo."""
        return cls.model.objects.filter(
            student_id=student_id, academic_period_id=academic_period_id
        ).first()
