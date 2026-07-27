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
    def batch_calculate(
        cls,
        academic_period_id: int,
        student_ids: list,
        user_id: Optional[int] = None,
        risk_type: str = "general",
    ):
        """
        Calcula riesgo en batch para múltiples estudiantes.
        """
        from apps.analytics.tasks import batch_calculate_academic_risk

        return batch_calculate_academic_risk.delay(
            academic_period_id, student_ids, user_id=user_id, risk_type=risk_type
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
        Evalúa reglas, ML y motor institucional con parámetros simulados.

        Retorna:
          - ``reglas``: score heurístico (siempre motor de reglas).
          - ``ml``: riesgo academico general estimado por el modelo institucional.
          - ``produccion``: resultado con el motor seleccionado en config.
          - ``config_simulacion``: pesos/umbrales usados en la simulación.
          - ``config_institucional``: configuración persistida en BD.
        """
        from dataclasses import replace

        from apps.analytics.services.risk_scoring_config_service import (
            RiskScoringConfigService,
        )
        from .risk_engine import (
            calculate_risk,
            _align_ml_score_to_rule_band,
            _predict_ml_score,
            score_to_risk_label,
        )

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

        avg_grade = params["average_grade"]
        metrics = {
            "attendance_rate": params["attendance_rate"],
            "consecutive_absences_max": params.get("consecutive_absences_max", 0),
            "tardiness_count": params.get("tardiness_count", 0),
            "justified_absences": params.get("justified_absences", 0),
            "unjustified_absences": params.get("unjustified_absences", 0),
            "avg_grade_normalized": avg_grade,
            "formative_avg_normalized": avg_grade,
            "summative_avg_normalized": avg_grade,
            "grade_trend_slope": params.get("grade_trend_slope", 0),
            "failing_subjects_count": params["failing_subjects_count"],
            "conduct_score": 10
            - (
                params.get("mild_incidents_count", 0) * 0.5
                + params.get("moderate_incidents_count", 0) * 1.0
                + params.get("severe_incidents_count", 0) * 2.0
            ),
            "severe_incidents_count": params.get("severe_incidents_count", 0),
            "family_notified_ratio": params.get("family_notified_ratio", 0),
            "prev_period_avg_grade": params.get("prev_period_avg_grade", 0),
            "age_grade_gap": params.get("age_grade_gap", 0),
            "is_repeat": params.get("is_repeat", False),
            "has_special_needs": params.get("has_special_needs", False),
        }

        overrides = params.get("config_overrides") or {}
        sim_config = RiskScoringConfigService.build_effective_from_dict(overrides)
        rules_config = replace(sim_config, engine="reglas")

        rules_result = calculate_risk(snapshot, metrics=metrics, config=rules_config)
        produccion_result = calculate_risk(snapshot, metrics=metrics, config=sim_config)

        ml_result: Dict[str, Any] = {}
        if params.get("try_ml", True):
            try:
                ml_score = _predict_ml_score(snapshot, metrics)
                if ml_score is not None:
                    puntaje = round(
                        float(
                            _align_ml_score_to_rule_band(
                                ml_score,
                                rules_result["semaforo_riesgo"]["nivel"],
                            )
                        ),
                        2,
                    )
                    ml_result = {
                        "puntaje_riesgo": puntaje,
                        "nivel": score_to_risk_label(puntaje),
                        "model_version": "sklearn-joblib-v3-institutional",
                    }
                else:
                    ml_result = {
                        "error": "Modelo no disponible. Entrena con: python manage.py train_risk_model"
                    }
            except Exception:
                ml_result = {"error": "Error al ejecutar modelo ML"}
        else:
            ml_result = {"error": "ML deshabilitado en esta simulación"}

        institucional = RiskScoringConfigService.get_effective()
        sim_preset = cls._resolve_simulation_preset(overrides)
        inst_preset = cls._resolve_institutional_preset()

        config_simulacion = cls._effective_config_to_api_dict(sim_config, sim_preset)

        reglas_model_version = rules_result["model_version"]
        if "sklearn" in reglas_model_version:
            from .risk_engine import MODEL_VERSION_FALLBACK

            reglas_model_version = (
                f"{MODEL_VERSION_FALLBACK}+{rules_config.version_tag or 'simulate'}"
            )

        return {
            "reglas": {
                "semaforo_riesgo": rules_result["semaforo_riesgo"],
                "detalle_por_variable": rules_result["detalle_por_variable"],
                "model_version": reglas_model_version,
                "motor": "reglas",
            },
            "ml": ml_result,
            "produccion": {
                "semaforo_riesgo": produccion_result["semaforo_riesgo"],
                "detalle_por_variable": produccion_result["detalle_por_variable"],
                "model_version": produccion_result["model_version"],
                "motor": sim_config.engine,
            },
            "config_simulacion": config_simulacion,
            "config_institucional": cls._effective_config_to_api_dict(
                institucional, inst_preset
            ),
        }

    @classmethod
    def simulate_subject(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        from apps.analytics.ml.subject_features import (
            SUBJECT_CODE_MAP,
            SUBJECT_MODEL_PATH,
            TRAIN_SUBJECT_FEATURES,
            _to_number,
        )
        from apps.analytics.ml.subject_model import SUBJECT_FEATURE_LABELS

        raw = {
            **params,
            "subject_code_idx": SUBJECT_CODE_MAP.get(
                str(params.get("subject_code", "MAT")).upper(), 0
            ),
        }
        return cls._simulate_probability_model(
            model_path=SUBJECT_MODEL_PATH,
            expected_model_type="subject_risk",
            default_features=TRAIN_SUBJECT_FEATURES,
            raw=raw,
            labels=SUBJECT_FEATURE_LABELS,
            unavailable_message="Modelo por materia no entrenado",
            to_number=_to_number,
        )

    @classmethod
    def simulate_annual(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        from apps.analytics.ml.annual_features import (
            ANNUAL_MODEL_PATH,
            TRAIN_ANNUAL_FEATURES,
            _to_number,
        )
        from apps.analytics.ml.annual_model import ANNUAL_FEATURE_LABELS

        return cls._simulate_probability_model(
            model_path=ANNUAL_MODEL_PATH,
            expected_model_type="annual_risk",
            default_features=TRAIN_ANNUAL_FEATURES,
            raw=params,
            labels=ANNUAL_FEATURE_LABELS,
            unavailable_message="Modelo anual no entrenado",
            to_number=_to_number,
        )

    @classmethod
    def simulate_dropout(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        from apps.analytics.ml.dropout_features import (
            DROPOUT_FEATURE_LABELS,
            DROPOUT_MODEL_PATH,
            TRAIN_DROPOUT_FEATURES,
            _to_number,
        )

        return cls._simulate_probability_model(
            model_path=DROPOUT_MODEL_PATH,
            expected_model_type="dropout_risk",
            default_features=TRAIN_DROPOUT_FEATURES,
            raw=params,
            labels=DROPOUT_FEATURE_LABELS,
            unavailable_message="Modelo de desercion no entrenado",
            to_number=_to_number,
        )

    @staticmethod
    def _simulate_probability_model(
        *,
        model_path,
        expected_model_type: str,
        default_features: list[str],
        raw: Dict[str, Any],
        labels: Dict[str, str],
        unavailable_message: str,
        to_number,
    ) -> Dict[str, Any]:
        import joblib

        if not model_path.exists():
            return {"error": unavailable_message}

        try:
            artifact = joblib.load(model_path)
        except Exception:
            return {"error": "No se pudo cargar el artefacto del modelo"}

        if artifact.get("model_type") != expected_model_type:
            return {"error": "Artefacto incompatible. Reentrene este modelo."}

        model = artifact["model"]
        features = artifact.get("features", default_features)
        feature_dict = {col: to_number(raw.get(col, 0)) for col in features}
        row = [feature_dict[col] for col in features]

        try:
            try:
                import pandas as pd

                X = pd.DataFrame([feature_dict], columns=features)
            except ModuleNotFoundError:
                X = [row]

            proba = model.predict_proba(X)[0]
            classes = list(getattr(model, "classes_", [0, 1]))
            pos_idx = classes.index(1) if 1 in classes else len(classes) - 1
            probability = round(float(proba[pos_idx]) * 100, 2)
        except Exception:
            return {"error": "Error al ejecutar el modelo"}

        if probability < 30:
            level = "bajo"
        elif probability < 60:
            level = "medio"
        else:
            level = "alto"

        importances = artifact.get("feature_importances", [])
        factors = [
            {
                "feature": features[i],
                "label": labels.get(features[i], features[i]),
                "importance": round(float(importances[i]), 4)
                if i < len(importances)
                else 0,
                "value": float(feature_dict.get(features[i], 0)),
            }
            for i in range(len(features))
        ]
        factors.sort(key=lambda item: item["importance"], reverse=True)

        return {
            "probability": probability,
            "risk_level": level,
            "model_type": expected_model_type,
            "factors": [factor for factor in factors if factor["importance"] > 0][:5],
        }

    @staticmethod
    def _resolve_simulation_preset(overrides: dict) -> str:
        if overrides.get("preset"):
            return overrides["preset"]
        return StudentRiskCalculationService._resolve_institutional_preset()

    @staticmethod
    def _resolve_institutional_preset() -> str:
        try:
            from apps.analytics.student_risk.infrastructure.repositories import (
                RiskScoringConfigRepository,
            )

            db_row = RiskScoringConfigRepository.get_singleton()
            return db_row.preset if db_row else "equilibrado"
        except Exception:
            return "equilibrado"

    @staticmethod
    def _effective_config_to_api_dict(effective_config, preset: str) -> dict:
        """Convierte EffectiveScoringConfig a dict compatible con el serializer."""
        return {
            "engine": effective_config.engine,
            "preset": preset,
            "weight_conducta": round(effective_config.weight_conducta * 100, 2),
            "weight_asistencia": round(effective_config.weight_asistencia * 100, 2),
            "weight_calificaciones": round(
                effective_config.weight_calificaciones * 100, 2
            ),
            "attendance_red_max": effective_config.attendance_red_max,
            "attendance_yellow_max": effective_config.attendance_yellow_max,
            "attendance_green_min": effective_config.attendance_green_min,
            "average_red_max": effective_config.average_red_max,
            "average_yellow_max": effective_config.average_yellow_max,
            "average_green_min": effective_config.average_green_min,
            "severe_red_min": effective_config.severe_red_min,
            "mild_yellow_min": effective_config.mild_yellow_min,
            "severe_green_max": effective_config.severe_green_max,
            "mild_green_max": effective_config.mild_green_max,
        }
