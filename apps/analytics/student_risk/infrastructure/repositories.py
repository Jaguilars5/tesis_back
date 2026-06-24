"""
Implementación de repositorios para riesgo estudiantil.
"""

from typing import List, Optional

from apps.core.repositories.base import BaseRepository

from .models import (
    RiskFactor,
    StudentRiskScore,
    StudentRiskFactor,
    StudentFeatureSnapshot,
    RiskScoringConfig,
)


class RiskFactorRepository(BaseRepository):
    """Repositorio para catálogo de factores de riesgo."""

    model = RiskFactor

    @classmethod
    def get_by_code(cls, code: str) -> Optional[RiskFactor]:
        """Obtener factor por su código."""
        try:
            return cls.model.objects.get(code=code)
        except cls.model.DoesNotExist:
            return None


class StudentRiskScoreRepository(BaseRepository):
    """Repositorio para puntajes de riesgo de estudiantes."""

    model = StudentRiskScore

    @classmethod
    def get_all(cls, active_only: bool = True):
        """Obtener todos los puntajes con select_related para optimización."""
        qs = cls.model.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        return qs.select_related("enrollment", "academic_period")

    @classmethod
    def get_by_id(cls, pk: int) -> Optional[StudentRiskScore]:
        """Obtener puntaje por ID con relaciones."""
        try:
            return cls.model.objects.select_related(
                "enrollment", "academic_period"
            ).get(pk=pk)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_by_enrollment(cls, enrollment_id: int):
        """Obtener puntajes por matrícula."""
        return (
            cls.model.objects.filter(enrollment_id=enrollment_id)
            .select_related("academic_period")
            .order_by("-calculated_at")
        )

    @classmethod
    def get_by_period(cls, academic_period_id: int):
        """Obtener puntajes por período académico."""
        return cls.model.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment")

    @classmethod
    def get_by_risk_label(cls, academic_period_id: int, risk_label: str):
        """Obtener estudiantes con una etiqueta de riesgo específica."""
        return cls.model.objects.filter(
            academic_period_id=academic_period_id,
            risk_label=risk_label,
        ).select_related("enrollment")

    @classmethod
    def get_latest_for_enrollment(cls, enrollment_id: int) -> Optional[StudentRiskScore]:
        """Obtener el puntaje más reciente para una matrícula."""
        return (
            cls.model.objects.filter(enrollment_id=enrollment_id)
            .order_by("-calculated_at")
            .first()
        )


class StudentRiskFactorRepository(BaseRepository):
    """Repositorio para factores de riesgo por estudiante."""

    model = StudentRiskFactor

    @classmethod
    def get_by_score(cls, score_id: int):
        """Obtener factores asociados a un puntaje específico."""
        return cls.model.objects.filter(
            student_risk_score_id=score_id
        ).select_related("risk_factor")


class StudentFeatureSnapshotRepository(BaseRepository):
    """Repositorio para snapshots de features."""

    model = StudentFeatureSnapshot

    @classmethod
    def get_all(cls, active_only: bool = True):
        """Obtener todos los snapshots con relaciones."""
        qs = cls.model.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        return qs.select_related("enrollment", "academic_period")

    @classmethod
    def get_by_id(cls, pk: int) -> Optional[StudentFeatureSnapshot]:
        """Obtener snapshot por ID."""
        try:
            return cls.model.objects.select_related(
                "enrollment", "academic_period"
            ).get(pk=pk)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_current_for_enrollment(cls, enrollment_id: int, academic_period_id: int):
        """Obtener el snapshot actual para una matrícula y período."""
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
            is_current=True,
        ).first()

    @classmethod
    def get_by_period(cls, academic_period_id: int):
        """Obtener snapshots por período."""
        return cls.model.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment")


class RiskScoringConfigRepository:
    """
    Repositorio para la configuración singleton de scoring.

    No hereda de BaseRepository porque no usa el patrón CRUD estándar.
    """

    model = RiskScoringConfig

    @classmethod
    def get_or_create_singleton(cls) -> RiskScoringConfig:
        """Obtiene o crea la configuración singleton."""
        config, _ = cls.model.objects.get_or_create(
            pk=cls.model.SINGLETON_PK,
            defaults={
                "engine": cls.model.ScoringEngineChoices.RULES,
                "preset": cls.model.ScoringPresetChoices.EQUILIBRADO,
            },
        )
        return config

    @classmethod
    def get_singleton(cls) -> Optional[RiskScoringConfig]:
        """Obtiene la configuración singleton si existe."""
        try:
            return cls.model.objects.get(pk=cls.model.SINGLETON_PK)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def update_singleton(cls, **kwargs) -> RiskScoringConfig:
        """Actualiza la configuración singleton."""
        config = cls.get_or_create_singleton()
        for key, value in kwargs.items():
            setattr(config, key, value)
        config.save()
        return config
