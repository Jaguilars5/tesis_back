"""
Servicios de dominio para riesgo estudiantil.

Lógica de negocio pura que orquesta validaciones y persistencia.
"""

from typing import Any, Dict, Optional

from ..infrastructure.repositories import RiskScoringConfigRepository


class RiskScoringConfigService:
    """
    Servicio para gestión de configuración de scoring.

    Proporciona acceso al singleton y aplicación de presets. Los presets
    canónicos viven en ``apps.analytics.services.risk_scoring_config_service``
    (fuente única, consumida también por el motor de cálculo).
    """

    @classmethod
    def get_effective_config(cls):
        """Obtiene la configuración efectiva (singleton desde DB)."""
        return RiskScoringConfigRepository.get_or_create_singleton()

    @classmethod
    def apply_preset(cls, preset_name: str):
        """Aplica un preset predefinido a la configuración."""
        from apps.analytics.services.risk_scoring_config_service import PRESETS

        if preset_name not in PRESETS:
            raise ValueError(
                f"Preset '{preset_name}' no válido. "
                f"Opciones: {', '.join(PRESETS.keys())}"
            )

        config_data = dict(PRESETS[preset_name])
        config_data["preset"] = preset_name
        config_data.setdefault("engine", "reglas")
        return RiskScoringConfigRepository.update_singleton(**config_data)

    @classmethod
    def update_config(cls, **kwargs):
        """Actualiza campos específicos de la configuración."""
        # Si se actualiza algo distinto al preset, marcar como personalizado.
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

    @classmethod
    def simulate(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evalúa el motor/reglas con parámetros simulados (sin estudiante real).

        Retorna ``{"reglas": ..., "ml": ..., "config": <modelo singleton>}``;
        la serialización de ``config`` queda a cargo de la vista.
        """
        from .risk_engine import calculate_risk, _predict_ml_score

        variables = {
            "conducta": {
                "faltas_leves": params["mild_incidents_count"],
                "faltas_graves": params["severe_incidents_count"],
            },
            "asistencia": {
                "porcentaje_asistencia": params["attendance_rate"],
                "total_registros": 1,
            },
            "calificaciones": {
                "promedio_actual": params["average_grade"],
                "total_calificaciones": 1,
                "materias_reprobadas": params["failing_subjects_count"],
            },
        }
        snapshot = {
            "estudiante_id": "simulacion",
            "periodo": "simulacion",
            "variables": variables,
        }

        config = RiskScoringConfigService.get_effective_config()
        rules_result = calculate_risk(snapshot, config=config)

        ml_result = None
        if params.get("try_ml") and config.engine == "ML":
            try:
                ml_score = _predict_ml_score(snapshot)
                if ml_score is not None:
                    ml_result = {
                        "puntaje_riesgo": round(float(ml_score), 2),
                        "model_version": "sklearn-joblib-v2",
                    }
            except Exception:
                ml_result = {"error": "Error al ejecutar modelo ML"}

        return {
            "reglas": {
                "semaforo_riesgo": rules_result["semaforo_riesgo"],
                "detalle_por_variable": rules_result["detalle_por_variable"],
                "model_version": rules_result["model_version"],
            },
            "ml": ml_result,
            "config": config,
        }
