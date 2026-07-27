"""
Entrenamiento del modelo anual (modelo_riesgo_anual).

Predice la probabilidad de que un estudiante pierda el año
(1+ materia con annual_final_avg < 7.00) usando features disponibles
en un período académico intermedio.

Target: AnnualGradeSummary.is_failing (verdaderos anuales finalizados).

Ejecutar: python manage.py train_risk_model --annual-model
"""

import logging
from decimal import Decimal

from apps.analytics.student_risk.infrastructure.models import StudentFeatureSnapshot
from apps.grading.student_note.infrastructure.models import AnnualGradeSummary

from .annual_features import (
    ANNUAL_FEATURES,
    TRAIN_ANNUAL_FEATURES,
    ANNUAL_MODEL_PATH,
    _to_number,
)
from .training_params import build_training_params

logger = logging.getLogger(__name__)

ANNUAL_FEATURE_LABELS = {
    "period_index": "Periodo del año",
    "attendance_rate": "Asistencia general",
    "consecutive_absences_max": "Ausencias consecutivas",
    "tardiness_count": "Tardanzas",
    "justified_absences": "Faltas justificadas",
    "unjustified_absences": "Faltas injustificadas",
    "formative_avg_normalized": "Promedio formativo",
    "summative_avg_normalized": "Promedio sumativo",
    "grade_trend_slope": "Tendencia de notas",
    "failing_subjects_count": "Materias reprobadas",
    "conduct_score": "Conducta",
    "severe_incidents_count": "Incidentes graves",
    "family_notified_ratio": "Notificaci\u00f3n familiar",
    "prev_period_avg_grade": "Nota periodo anterior",
    "age_grade_gap": "Brecha edad-grado",
    "is_repeat": "Repitente",
    "has_special_needs": "Necesidades especiales",
}


class AnnualRiskModelTrainer:

    FEATURES = TRAIN_ANNUAL_FEATURES

    def _get_period_index(self, academic_period):
        """Obtiene el índice del período dentro del año escolar (1, 2, 3...)."""
        from apps.academic.academic_period.infrastructure.repositories import (
            AcademicPeriodRepository,
        )

        periods = AcademicPeriodRepository.get_by_school_year(
            academic_period.school_year_id
        ).order_by("start_date")
        for idx, p in enumerate(periods, start=1):
            if p.id == academic_period.id:
                return idx
        return 1

    def train(self, model_path=None, training_params=None):
        import joblib
        import pandas as pd
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score, StratifiedKFold
        from sklearn.metrics import classification_report

        annual_summaries = AnnualGradeSummary.objects.filter(
            is_finalized=True,
        ).select_related("enrollment", "school_year")

        total_annual = annual_summaries.count()
        logger.info("Resúmenes anuales finalizados encontrados: %d", total_annual)
        if total_annual == 0:
            raise ValueError("No hay resúmenes anuales finalizados para entrenar")

        X, y = [], []
        skipped = 0

        for annual in annual_summaries:
            snapshots = (
                StudentFeatureSnapshot.objects.filter(
                    enrollment_id=annual.enrollment_id,
                    academic_period__school_year=annual.school_year,
                )
                .select_related("academic_period")
                .order_by("academic_period__start_date")
            )

            if not snapshots.exists():
                skipped += 1
                continue

            target = 1 if annual.is_failing else 0

            for snapshot in snapshots:
                period_idx = self._get_period_index(snapshot.academic_period)

                features = {
                    "period_index": period_idx,
                    "attendance_rate": _to_number(snapshot.attendance_rate),
                    "consecutive_absences_max": _to_number(
                        snapshot.consecutive_absences_max
                    ),
                    "tardiness_count": _to_number(snapshot.tardiness_count),
                    "justified_absences": _to_number(snapshot.justified_absences),
                    "unjustified_absences": _to_number(snapshot.unjustified_absences),
                    "formative_avg_normalized": _to_number(
                        snapshot.formative_avg_normalized
                    ),
                    "summative_avg_normalized": _to_number(
                        snapshot.summative_avg_normalized
                    ),
                    "grade_trend_slope": _to_number(snapshot.grade_trend_slope),
                    "failing_subjects_count": _to_number(
                        snapshot.failing_subjects_count
                    ),
                    "conduct_score": _to_number(snapshot.conduct_score),
                    "severe_incidents_count": _to_number(
                        snapshot.severe_incidents_count
                    ),
                    "family_notified_ratio": _to_number(snapshot.family_notified_ratio),
                    "prev_period_avg_grade": _to_number(snapshot.prev_period_avg_grade),
                    "age_grade_gap": _to_number(snapshot.age_grade_gap),
                    "is_repeat": _to_number(snapshot.is_repeat),
                    "has_special_needs": _to_number(snapshot.has_special_needs),
                }

                row = [features[col] for col in self.FEATURES]
                X.append(row)
                y.append(target)

        if skipped:
            logger.info("Estudiantes omitidos (sin snapshots en el año): %d", skipped)

        logger.info(
            "Pares (X, y) generados: %d (target=1: %d, target=0: %d)",
            len(X),
            sum(y),
            len(X) - sum(y),
        )

        if len(X) < 100:
            raise ValueError(f"Datos insuficientes: solo {len(X)} registros")

        df = pd.DataFrame(X, columns=self.FEATURES).fillna(0)

        logger.info("Estadísticas descriptivas:\n%s", df.describe())

        params = build_training_params(**(training_params or {}))

        model = RandomForestClassifier(
            n_estimators=params.n_estimators,
            max_depth=params.max_depth,
            min_samples_leaf=params.min_samples_leaf,
            class_weight=params.class_weight,
            random_state=params.random_state,
            n_jobs=params.n_jobs,
        )

        cv = StratifiedKFold(
            n_splits=params.cv_splits,
            shuffle=True,
            random_state=params.random_state,
        )
        cv_scores = cross_val_score(model, df, y, cv=cv, scoring="roc_auc")
        logger.info("CV ROC-AUC: %.4f (±%.4f)", cv_scores.mean(), cv_scores.std())

        model.fit(df, y)

        y_pred = model.predict(df)
        logger.info(
            "Classification report (train):\n%s",
            classification_report(y, y_pred, target_names=["aprueba", "pierde_año"]),
        )

        importance_df = pd.DataFrame(
            {
                "feature": self.FEATURES,
                "importance": model.feature_importances_,
            }
        ).sort_values("importance", ascending=False)
        logger.info("Feature importances:\n%s", importance_df)

        artifact = {
            "model": model,
            "features": self.FEATURES,
            "feature_importances": model.feature_importances_.tolist(),
            "model_type": "annual_risk",
            "training_params": params.__dict__,
        }

        target_path = model_path or ANNUAL_MODEL_PATH
        joblib.dump(artifact, target_path)
        logger.info("Modelo anual guardado en: %s", target_path)

        return model

    @classmethod
    def predict(cls, enrollment_id, academic_period_id):
        """Predice la probabilidad de que un estudiante pierda el año.

        Args:
            enrollment_id: ID de la matrícula
            academic_period_id: ID del período académico actual

        Returns:
            Dict con probability (0-100) y risk_level
            o None si no hay modelo o snapshot.
        """
        import joblib

        if not ANNUAL_MODEL_PATH.exists():
            logger.warning("Modelo anual no encontrado en %s", ANNUAL_MODEL_PATH)
            return None

        try:
            artifact = joblib.load(ANNUAL_MODEL_PATH)
            model = artifact["model"]
            features_list = artifact["features"]
        except Exception as e:
            logger.error("Error cargando modelo anual: %s", e)
            return None

        snapshot = (
            StudentFeatureSnapshot.objects.filter(
                enrollment_id=enrollment_id,
                academic_period_id=academic_period_id,
            )
            .select_related("academic_period")
            .first()
        )

        if not snapshot:
            return None

        trainer = cls()
        period_idx = trainer._get_period_index(snapshot.academic_period)

        features = {
            "period_index": period_idx,
            "attendance_rate": _to_number(snapshot.attendance_rate),
            "consecutive_absences_max": _to_number(snapshot.consecutive_absences_max),
            "tardiness_count": _to_number(snapshot.tardiness_count),
            "justified_absences": _to_number(snapshot.justified_absences),
            "unjustified_absences": _to_number(snapshot.unjustified_absences),
            "formative_avg_normalized": _to_number(snapshot.formative_avg_normalized),
            "summative_avg_normalized": _to_number(snapshot.summative_avg_normalized),
            "grade_trend_slope": _to_number(snapshot.grade_trend_slope),
            "failing_subjects_count": _to_number(snapshot.failing_subjects_count),
            "conduct_score": _to_number(snapshot.conduct_score),
            "severe_incidents_count": _to_number(snapshot.severe_incidents_count),
            "family_notified_ratio": _to_number(snapshot.family_notified_ratio),
            "prev_period_avg_grade": _to_number(snapshot.prev_period_avg_grade),
            "age_grade_gap": _to_number(snapshot.age_grade_gap),
            "is_repeat": _to_number(snapshot.is_repeat),
            "has_special_needs": _to_number(snapshot.has_special_needs),
        }

        row = [features[col] for col in features_list]

        import numpy as np

        proba = model.predict_proba([row])[0]
        prob_positive = float(proba[1]) if model.classes_[1] == 1 else float(proba[0])

        if prob_positive < 0.3:
            risk_level = "bajo"
        elif prob_positive < 0.6:
            risk_level = "medio"
        else:
            risk_level = "alto"

        importances = artifact.get("feature_importances", [])
        factors = [
            {
                "feature": features_list[i],
                "label": ANNUAL_FEATURE_LABELS.get(features_list[i], features_list[i]),
                "importance": (
                    round(float(importances[i]), 4) if i < len(importances) else 0
                ),
                "value": float(features.get(features_list[i], 0)),
            }
            for i in range(len(features_list))
        ]
        factors.sort(key=lambda f: f["importance"], reverse=True)
        top_factors = [f for f in factors if f["importance"] > 0][:5]

        return {
            "probability": round(prob_positive * 100, 2),
            "risk_level": risk_level,
            "factors": top_factors,
        }
