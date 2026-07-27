"""
Entrenamiento del modelo general de riesgo academico institucional.

El modelo general debe medir el mismo constructo que el motor de reglas:
riesgo academico integral 0-100 / semaforo institucional. Por eso el target
se genera aplicando las reglas sobre cada StudentFeatureSnapshot historico, no
desde PeriodGradeSummary.is_failing. Los modelos por materia y anual conservan
sus objetivos especializados de reprobacion/perdida del anio.

Ejecutar: python manage.py train_risk_model
"""

import logging
from collections import Counter
from dataclasses import asdict, replace

from apps.analytics.student_risk.infrastructure.models import StudentFeatureSnapshot

from .features import MODEL_PATH, TRAIN_FEATURES, _to_number
from .training_params import build_training_params

logger = logging.getLogger(__name__)

RISK_LABEL_TO_CLASS = {"verde": 0, "amarillo": 1, "rojo": 2}
RISK_CLASS_TO_LABEL = {value: key for key, value in RISK_LABEL_TO_CLASS.items()}
SCORE_CLASS_CENTERS = {0: 20.0, 1: 55.0, 2: 85.0}


class RiskModelTrainer:
    """Entrena el RandomForest general contra el semaforo institucional."""

    FEATURES = TRAIN_FEATURES

    @staticmethod
    def _snapshot_average(snapshot) -> float:
        values = [
            _to_number(snapshot.formative_avg_normalized),
            _to_number(snapshot.summative_avg_normalized),
        ]
        non_zero = [value for value in values if value > 0]
        return sum(non_zero) / len(non_zero) if non_zero else 0.0

    @staticmethod
    def _conduct_counts_from_snapshot(snapshot) -> dict:
        severe = int(_to_number(snapshot.severe_incidents_count))
        conduct_score = _to_number(snapshot.conduct_score)
        penalty = max(0.0, 10.0 - conduct_score)
        remaining_penalty = max(0.0, penalty - severe * 2.0)
        inferred_mild = int(round(remaining_penalty / 0.5))
        return {
            "faltas_leves": inferred_mild,
            "faltas_moderadas": 0,
            "faltas_graves": severe,
        }

    @classmethod
    def _variables_from_snapshot(cls, snapshot) -> dict:
        return {
            "conducta": cls._conduct_counts_from_snapshot(snapshot),
            "asistencia": {
                "porcentaje_asistencia": _to_number(snapshot.attendance_rate),
                "total_registros": 1,
                "max_faltas_consecutivas": int(
                    _to_number(snapshot.consecutive_absences_max)
                ),
                "tardanzas": int(_to_number(snapshot.tardiness_count)),
                "faltas_justificadas": int(_to_number(snapshot.justified_absences)),
                "faltas_injustificadas": int(
                    _to_number(snapshot.unjustified_absences)
                ),
            },
            "calificaciones": {
                "promedio_actual": cls._snapshot_average(snapshot),
                "total_calificaciones": 1,
                "materias_reprobadas": int(
                    _to_number(snapshot.failing_subjects_count)
                ),
                "tendencia_notas": _to_number(snapshot.grade_trend_slope),
            },
        }

    @classmethod
    def _get_rules_target(cls, snapshot, config) -> tuple[int, float, str]:
        from apps.analytics.student_risk.domain.risk_engine import (
            _fallback_risk_score,
            _risk_level,
        )

        variables = cls._variables_from_snapshot(snapshot)
        label = _risk_level(variables, config)
        score = _fallback_risk_score(variables, label, config)
        return RISK_LABEL_TO_CLASS[label], round(float(score), 2), label

    def train(self, model_path=None, training_params=None):
        import joblib
        import pandas as pd
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import classification_report, confusion_matrix
        from sklearn.model_selection import StratifiedKFold, cross_val_score

        from apps.analytics.services.risk_scoring_config_service import (
            RiskScoringConfigService,
        )

        snapshots = StudentFeatureSnapshot.objects.all()
        total_snapshots = snapshots.count()
        logger.info("Total snapshots encontrados: %d", total_snapshots)
        if total_snapshots == 0:
            raise ValueError("No hay snapshots para entrenar")

        rules_config = replace(RiskScoringConfigService.get_effective(), engine="reglas")
        X, y, y_scores = [], [], []

        for snapshot in snapshots:
            target, rules_score, _label = self._get_rules_target(snapshot, rules_config)
            row = [_to_number(getattr(snapshot, col, 0)) for col in self.FEATURES]
            X.append(row)
            y.append(target)
            y_scores.append(rules_score)

        logger.info("Pares (X, y) generados: %d", len(X))
        target_counts = Counter(y)
        logger.info(
            "Distribucion target institucional: %s",
            {
                RISK_CLASS_TO_LABEL[key]: target_counts.get(key, 0)
                for key in sorted(RISK_CLASS_TO_LABEL)
            },
        )

        if len(X) < 100:
            raise ValueError(f"Datos insuficientes: solo {len(X)} registros")
        if len(target_counts) < 2:
            raise ValueError(
                "Datos insuficientes: el target institucional tiene una sola clase"
            )

        df = pd.DataFrame(X, columns=self.FEATURES).fillna(0)
        logger.info("Estadisticas descriptivas:\n%s", df.describe())

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
        cv_accuracy = cross_val_score(model, df, y, cv=cv, scoring="accuracy")
        cv_f1 = cross_val_score(model, df, y, cv=cv, scoring="f1_weighted")
        logger.info("CV Accuracy: %.4f (+/- %.4f)", cv_accuracy.mean(), cv_accuracy.std())
        logger.info("CV F1 weighted: %.4f (+/- %.4f)", cv_f1.mean(), cv_f1.std())

        model.fit(df, y)

        y_pred = model.predict(df)
        logger.info(
            "Classification report (train):\n%s",
            classification_report(
                y,
                y_pred,
                labels=[0, 1, 2],
                target_names=["verde", "amarillo", "rojo"],
                zero_division=0,
            ),
        )
        logger.info(
            "Confusion matrix (train, labels verde/amarillo/rojo):\n%s",
            confusion_matrix(y, y_pred, labels=[0, 1, 2]),
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
            "model_type": "general_institutional_risk",
            "target": "rules_risk_label/rules_risk_score",
            "risk_label_to_class": RISK_LABEL_TO_CLASS,
            "risk_class_to_label": RISK_CLASS_TO_LABEL,
            "score_class_centers": SCORE_CLASS_CENTERS,
            "rules_config": asdict(rules_config),
            "training_params": params.__dict__,
            "training_metrics": {
                "cv_accuracy_mean": float(cv_accuracy.mean()),
                "cv_accuracy_std": float(cv_accuracy.std()),
                "cv_f1_weighted_mean": float(cv_f1.mean()),
                "cv_f1_weighted_std": float(cv_f1.std()),
                "target_distribution": {
                    RISK_CLASS_TO_LABEL[key]: target_counts.get(key, 0)
                    for key in sorted(RISK_CLASS_TO_LABEL)
                },
                "rules_score_min": min(y_scores),
                "rules_score_max": max(y_scores),
            },
        }

        target_path = model_path or MODEL_PATH
        joblib.dump(artifact, target_path)
        logger.info("Modelo guardado en: %s", target_path)

        return model
