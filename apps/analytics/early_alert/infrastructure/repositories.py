"""
Implementación de repositorios para alertas tempranas.
"""

from typing import List, Optional

from apps.core.repositories.base import BaseRepository

from ..domain.repositories import EarlyAlertRepositoryInterface
from ..domain.entities import EarlyAlertEntity
from .models import EarlyAlert
from .mappers import to_entity


class EarlyAlertRepository(BaseRepository, EarlyAlertRepositoryInterface):
    """
    Repositorio para EarlyAlert con operaciones CRUD y queries específicas.
    """

    model = EarlyAlert

    @classmethod
    def get_all(cls, active_only: bool = True) -> List[EarlyAlert]:
        """Obtener todas las alertas, opcionalmente solo activas."""
        qs = cls.model.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        return qs.select_related("enrollment", "academic_period", "attended_by_user")

    @classmethod
    def get_by_id(cls, pk: int) -> Optional[EarlyAlert]:
        """Obtener alerta por ID."""
        try:
            return cls.model.objects.select_related(
                "enrollment", "academic_period", "attended_by_user"
            ).get(pk=pk)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_pending_alerts(
        cls, urgency_level: Optional[str] = None
    ) -> List[EarlyAlert]:
        """Obtener alertas pendientes, filtradas opcionalmente por nivel de urgencia."""
        filters = {"attended": False}
        if urgency_level:
            filters["urgency_level"] = urgency_level
        return (
            cls.model.objects.filter(**filters)
            .select_related("enrollment", "academic_period")
            .order_by("-detected_at")
        )

    @classmethod
    def get_by_enrollment(cls, enrollment_id: int) -> List[EarlyAlert]:
        """Obtener alertas por matrícula."""
        return (
            cls.model.objects.filter(enrollment_id=enrollment_id)
            .select_related("enrollment", "academic_period")
            .order_by("-detected_at")
        )

    @classmethod
    def count_active_by_enrollment(cls, enrollment_id: int) -> int:
        """Contar alertas activas (no atendidas) por matrícula."""
        return cls.model.objects.filter(
            enrollment_id=enrollment_id, attended=False
        ).count()

    @classmethod
    def get_pending_count(cls) -> int:
        """Contar total de alertas pendientes."""
        return cls.model.objects.filter(attended=False).count()

    @classmethod
    def get_by_urgency(cls, urgency_level: str) -> List[EarlyAlert]:
        """Obtener alertas por nivel de urgencia."""
        return (
            cls.model.objects.filter(urgency_level=urgency_level)
            .select_related("enrollment", "academic_period")
            .order_by("-detected_at")
        )
