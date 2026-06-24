"""
Interfaces de repositorio (Abstract Base Classes) para alertas tempranas.

Define el contrato que deben implementar los repositorios de infraestructura.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..infrastructure.models import EarlyAlert


class EarlyAlertRepositoryInterface(ABC):
    """
    Interface para el repositorio de alertas tempranas.

    Todas las operaciones de persistencia deben pasar por esta interface.
    """

    @classmethod
    @abstractmethod
    def get_all(cls, active_only: bool = True) -> List[EarlyAlert]:
        """Obtener todas las alertas."""
        pass

    @classmethod
    @abstractmethod
    def get_by_id(cls, pk: int) -> Optional[EarlyAlert]:
        """Obtener alerta por ID."""
        pass

    @classmethod
    @abstractmethod
    def get_pending_alerts(
        cls, urgency_level: Optional[str] = None
    ) -> List[EarlyAlert]:
        """Obtener alertas pendientes."""
        pass

    @classmethod
    @abstractmethod
    def get_by_enrollment(cls, enrollment_id: int) -> List[EarlyAlert]:
        """Obtener alertas por matrícula."""
        pass

    @classmethod
    @abstractmethod
    def count_active_by_enrollment(cls, enrollment_id: int) -> int:
        """Contar alertas activas por matrícula."""
        pass
