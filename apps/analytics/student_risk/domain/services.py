"""
Servicios de dominio para riesgo estudiantil.

Lógica de negocio pura que orquesta validaciones y persistencia.
"""

from typing import Dict, Optional, Any
from decimal import Decimal

from ..infrastructure.repositories import (
    RiskScoringConfigRepository,
    StudentRiskScoreRepository,
    StudentFeatureSnapshotRepository,
)


# Presets de configuración (Auditoría §9.4)
PRESETS: Dict[str, Dict] = {
    "conservador": {
        "engine": "reglas",
        "preset": "conservador",
        "weight_conducta": Decimal("25.00"),
        "weight_asistencia": Decimal("40.00"),
        "weight_calificaciones": Decimal("35.00"),
        "attendance_red_max": Decimal("75.00"),
        "attendance_yellow_max": Decimal("88.00"),
        "average_red_max": Decimal("6.50"),
        "average_yellow_max": Decimal("7.50"),
        "severe_red_min": 2,
        "mild_yellow_min": 4,
    },
    "equilibrado": {
        "engine": "reglas",
        "preset": "equilibrado",
        "weight_conducta": Decimal("30.00"),
        "weight_asistencia": Decimal("35.00"),
        "weight_calificaciones": Decimal("35.00"),
        "attendance_red_max": Decimal("70.00"),
        "attendance_yellow_max": Decimal("85.00"),
        "average_red_max": Decimal("6.00"),
        "average_yellow_max": Decimal("7.00"),
        "severe_red_min": 3,
        "mild_yellow_min": 5,
    },
    "estricto": {
        "engine": "reglas",
        "preset": "estricto",
        "weight_conducta": Decimal("35.00"),
        "weight_asistencia": Decimal("30.00"),
        "weight_calificaciones": Decimal("35.00"),
        "attendance_red_max": Decimal("65.00"),
        "attendance_yellow_max": Decimal("80.00"),
        "average_red_max": Decimal("5.50"),
        "average_yellow_max": Decimal("6.50"),
        "severe_red_min": 4,
        "mild_yellow_min": 6,
    },
}


class RiskScoringConfigService:
    """
    Servicio para gestión de configuración de scoring.

    Proporciona acceso al singleton y aplicación de presets.
    """

    @classmethod
    def get_effective_config(cls):
        """Obtiene la configuración efectiva (singleton desde DB)."""
        return RiskScoringConfigRepository.get_or_create_singleton()

    @classmethod
    def apply_preset(cls, preset_name: str) -> Optional:
        """Aplica un preset predefinido a la configuración."""
        if preset_name not in PRESETS:
            raise ValueError(f"Preset '{preset_name}' no válido. Opciones: {', '.join(PRESETS.keys())}")

        config_data = PRESETS[preset_name].copy()
        return RiskScoringConfigRepository.update_singleton(**config_data)

    @classmethod
    def update_config(cls, **kwargs):
        """Actualiza campos específicos de la configuración."""
        # Si se actualiza algo distinto al preset, marcar como personalizado
        if any(k != "preset" for k in kwargs.keys()):
            kwargs["preset"] = "personalizado"
        return RiskScoringConfigRepository.update_singleton(**kwargs)


class StudentRiskCalculationService:
    """
    Servicio para cálculo de riesgo estudiantil.

    Coordinador que delega a feature_builder y el motor de scoring.
    """

    @classmethod
    def calculate_risk(cls, enrollment_id: int, academic_period_id: int, user_id: Optional[int] = None):
        """
        Calcula el riesgo para un estudiante.

        Retorna el task de Celery para ejecución asíncrona.
        """
        # Importación tardía para evitar ciclos
        from apps.analytics.tasks import calculate_student_academic_risk_task

        return calculate_student_academic_risk_task.delay(
            enrollment_id, academic_period_id, user_id=user_id
        )

    @classmethod
    def batch_calculate(cls, academic_period_id: int, student_ids: list, user_id: Optional[int] = None):
        """
        Calcula riesgo en batch para múltiples estudiantes.
        """
        from apps.analytics.tasks import batch_calculate_academic_risk

        return batch_calculate_academic_risk.delay(
            academic_period_id, student_ids, user_id=user_id
        )

    @classmethod
    def perform_risk_calculation(
        cls,
        student_id: int,
        academic_period_id: int,
    ) -> Dict[str, Any]:
        """
        Realiza el cálculo de riesgo sincrónicamente.

        Usado por tasks.py. Retorna el análisis completo.
        """
        from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder
        from .risk_engine import calculate_risk

        builder = AcademicRiskFeatureBuilder(student_id, academic_period_id)
        snapshot = builder.build()
        metrics = builder.build_persistence_metrics(snapshot)

        # El motor lee/normaliza la config efectiva internamente.
        analysis = calculate_risk(snapshot, metrics)

        return {
            "snapshot": snapshot,
            "metrics": metrics,
            "analysis": analysis,
        }


class AnalyticsService:
    """Lecturas agregadas del perfil de riesgo de un estudiante."""

    @staticmethod
    def get_student_risk_profile(student_id: int) -> Dict[str, Any]:
        """Retorna el score más reciente y su snapshot de métricas asociado."""
        risk = StudentRiskScoreRepository.get_latest_by_student(student_id)
        snapshot = None
        if risk:
            snapshot = StudentFeatureSnapshotRepository.get_by_student_period(
                student_id, risk.academic_period_id
            )
        return {"risk_score": risk, "metrics_snapshot": snapshot}

    @staticmethod
    def list_priority_students(academic_period_id: int):
        """Lista estudiantes con mayor riesgo en un periodo."""
        return StudentRiskScoreRepository.list_high_risk(academic_period_id)
