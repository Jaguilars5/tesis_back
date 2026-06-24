"""
Entities de dominio para riesgo estudiantil.

Dataclasses inmutables que representan el estado del dominio.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class RiskFactorEntity:
    """Entity inmutable para factores de riesgo catalogados."""

    id: Optional[int] = None
    code: str = ""
    name: str = ""
    description: str = ""


@dataclass(frozen=True)
class StudentRiskScoreEntity:
    """Entity inmutable para puntajes de riesgo."""

    id: Optional[int] = None
    enrollment_id: int = 0
    academic_period_id: int = 0
    risk_score: Decimal = Decimal("0.00")
    risk_label: str = ""
    model_version: str = ""
    calculated_at: Optional[datetime] = None

    def is_high_risk(self) -> bool:
        """Retorna True si el riesgo es alto (rojo)."""
        return self.risk_label == "rojo"

    def is_medium_risk(self) -> bool:
        """Retorna True si el riesgo es medio (amarillo)."""
        return self.risk_label == "amarillo"

    def is_low_risk(self) -> bool:
        """Retorna True si el riesgo es bajo (verde)."""
        return self.risk_label == "verde"


@dataclass(frozen=True)
class StudentRiskFactorEntity:
    """Entity inmutable para relación score-factor."""

    id: Optional[int] = None
    student_risk_score_id: int = 0
    risk_factor_id: int = 0
    contribution_weight: Decimal = Decimal("0.00")


@dataclass(frozen=True)
class StudentFeatureSnapshotEntity:
    """Entity inmutable para snapshots de features."""

    id: Optional[int] = None
    enrollment_id: int = 0
    academic_period_id: int = 0
    attendance_rate: Decimal = Decimal("0.00")
    consecutive_absences_max: int = 0
    tardiness_count: int = 0
    justified_absences: int = 0
    unjustified_absences: int = 0
    formative_avg_normalized: Decimal = Decimal("0.00")
    summative_avg_normalized: Decimal = Decimal("0.00")
    grade_trend_slope: Decimal = Decimal("0.00")
    failing_subjects_count: int = 0
    conduct_score: Decimal = Decimal("0.00")
    severe_incidents_count: int = 0
    family_notified_ratio: Decimal = Decimal("0.00")
    prev_period_avg_grade: Optional[Decimal] = None
    age_grade_gap: int = 0
    is_repeat: bool = False
    has_special_needs: bool = False
    is_current: bool = False
    snapshot_trigger: str = "MANUAL"
    calculated_at: Optional[datetime] = None


@dataclass(frozen=True)
class RiskScoringConfigEntity:
    """Entity inmutable para configuración de scoring."""

    id: int = 1  # Singleton
    engine: str = "reglas"
    preset: str = "equilibrado"
    weight_conducta: Decimal = Decimal("30.00")
    weight_asistencia: Decimal = Decimal("35.00")
    weight_calificaciones: Decimal = Decimal("35.00")
    attendance_red_max: Decimal = Decimal("70.00")
    attendance_yellow_max: Decimal = Decimal("85.00")
    average_red_max: Decimal = Decimal("6.00")
    average_yellow_max: Decimal = Decimal("7.00")
    severe_red_min: int = 3
    mild_yellow_min: int = 5
