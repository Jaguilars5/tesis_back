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
        Evalúa ambos motores con parámetros simulados.

        Retorna:
          - ``reglas``: score heurístico + factores críticos + recomendaciones.
          - ``ml``: probabilidad estimada de reprobar (regresión logística) o error.
          - ``config``: configuración activa del motor de riesgo.
        """
        from .risk_engine import calculate_risk, _predict_ml_score

        variables = {
            "conducta": {
                "faltas_leves": params.get("mild_incidents_count", 0),
                "faltas_moderadas": params.get("moderate_incidents_count", 0),
                "faltas_graves": params.get("severe_incidents_count", 0),
            },
            "asistencia": {
                "porcentaje_asistencia": params["attendance_rate"],
                "total_registros": 1,
                "max_faltas_consecutivas": params.get("consecutive_absences_max", 0),
                "tardanzas": params.get("tardiness_count", 0),
                "faltas_justificadas": params.get("justified_absences", 0),
                "faltas_injustificadas": params.get("unjustified_absences", 0),
            },
            "calificaciones": {
                "promedio_actual": params["average_grade"],
                "total_calificaciones": 1,
                "materias_reprobadas": params["failing_subjects_count"],
                "tendencia_notas": params.get("grade_trend_slope", 0),
            },
        }

        snapshot = {
            "estudiante_id": "simulacion",
            "periodo": "simulacion",
            "variables": variables,
        }

        metrics = {
            "attendance_rate": params["attendance_rate"],
            "consecutive_absences_max": params.get("consecutive_absences_max", 0),
            "tardiness_count": params.get("tardiness_count", 0),
            "justified_absences": params.get("justified_absences", 0),
            "unjustified_absences": params.get("unjustified_absences", 0),
            "avg_grade_normalized": params["average_grade"],
            "grade_trend_slope": params.get("grade_trend_slope", 0),
            "failing_subjects_count": params["failing_subjects_count"],
            "conduct_score": 10 - (params.get("mild_incidents_count", 0) * 0.5 + params.get("moderate_incidents_count", 0) * 1.0 + params.get("severe_incidents_count", 0) * 2.0),
            "severe_incidents_count": params.get("severe_incidents_count", 0),
            "family_notified_ratio": params.get("family_notified_ratio", 0),
            "prev_period_avg_grade": params.get("prev_period_avg_grade", 0),
            "age_grade_gap": params.get("age_grade_gap", 0),
            "is_repeat": params.get("is_repeat", False),
            "has_special_needs": params.get("has_special_needs", False),
        }

        config = RiskScoringConfigService.get_effective_config()
        rules_result = calculate_risk(snapshot, config=config)

        ml_result: Dict[str, Any] = {}
        try:
            ml_score = _predict_ml_score(snapshot, metrics)
            if ml_score is not None:
                ml_result = {
                    "puntaje_riesgo": round(float(ml_score), 2),
                    "model_version": "sklearn-joblib-v2",
                }
            else:
                ml_result = {"error": "Modelo no disponible. Entrena con: python manage.py train_risk_model"}
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
