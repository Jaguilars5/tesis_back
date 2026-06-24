"""
Entities de dominio para alertas tempranas.

Dataclasses inmutables que representan el estado del dominio.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class EarlyAlertEntity:
    """
    Entity inmutable para alertas tempranas.

    Representa el estado completo de una alerta sin dependencias de Django ORM.
    """

    id: Optional[int] = None
    enrollment_id: int = 0
    academic_period_id: int = 0
    alert_type: Optional[str] = None
    description: str = ""
    urgency_level: Optional[str] = None
    attended: bool = False
    attended_by_user_id: Optional[int] = None
    detected_at: Optional[datetime] = None
    attended_at: Optional[datetime] = None
    response_actions: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_pending(self) -> bool:
        """Retorna True si la alerta no ha sido atendida."""
        return not self.attended

    def has_high_urgency(self) -> bool:
        """Retorna True si la alerta es de alta urgencia o crítica."""
        return self.urgency_level in ("high", "critical")


@dataclass(frozen=True)
class EarlyAlertEvaluationResult:
    """Resultado de la evaluación de alertas para un estudiante."""

    alerts_created: list = field(default_factory=list)
    total_alerts: int = 0
