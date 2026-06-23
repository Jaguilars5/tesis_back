"""Repositorio del singleton de configuración del motor de riesgo (Fase 5)."""

from apps.core.repositories.base import BaseRepository
from ..models import RiskScoringConfig


class RiskScoringConfigRepository(BaseRepository):
    model = RiskScoringConfig

    @classmethod
    def get_singleton(cls):
        """Devuelve la fila singleton si existe, o None."""
        return cls.model.objects.filter(pk=cls.model.SINGLETON_PK).first()

    @classmethod
    def get_or_create_singleton(cls):
        """Devuelve la fila singleton, creándola con defaults si no existe."""
        obj, _ = cls.model.objects.get_or_create(pk=cls.model.SINGLETON_PK)
        return obj
