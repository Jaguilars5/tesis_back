"""
Entrenamiento y prediccion del modelo de riesgo de desercion escolar.

Este modelo es especializado: estima abandono/no continuidad, no reemplaza al
riesgo academico general institucional.
"""

import logging
from collections import Counter

from apps.analytics.student_risk.infrastructure.models import StudentFeatureSnapshot
from apps.students.infrastructure.models import EnrollmentStatusChoices

from .dropout_features import (
    DROPOUT_FEATURE_LABELS,
    DROPOUT_MODEL_PATH,
    TRAIN_DROPOUT_FEATURES,
    _to_number,
)
from .training_params import build_training_params

logger = logging.getLogger(__name__)

NON_DROPOUT_REASON_TOKENS = (
    "TRAS",
    "TRANSFER",
    "CAMBIO",
    "GRAD",
    "PROM",
    "PROMOC",
)


def dropout_level(probability: float) -> str:
    if probability < 30:
        return "bajo"
    if probability < 60:
        return "medio"
    return "alto"


class DropoutRiskModelTrainer:
    FEATURES = TRAIN_DROPOUT_FEATURES

    @staticmethod
    def _is_dropout(enrollment) -> int:
        status = enrollment.enrollment_status
        if status not in (
            EnrollmentStatusChoices.WITHDRAWN,
            EnrollmentStatusChoices.INACTIVE,
        ):
            return 0

        reason = getattr(enrollment, "withdrawal_reason", None)
        reason_text = " ".join(
            str(value or "").upper()
            for value in (
                getattr(reason, "code", ""),
                getattr(reason, "name", ""),
                getattr(reason, "description", ""),
            )
        )
        if any(token in reason_text for token in NON_DROPOUT_REASON_TOKENS):
            return 0
        return 1

    @staticmethod
    def _row_from_snapshot(snapshot, features):
        return [_to_number(getattr(snapshot, col, 0)) for col in features]

    def train(self, model_path=None, training_params=None):
        import joblib
        import pandas as pd
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import classification_report, confusion_matrix
        from sklearn.model_selection import StratifiedKFold, cross_val_score

        snapshots = StudentFeatureSnapshot.objects.select_related(
            "enrollment__withdrawal_reason"
        ).all()
        total = snapshots.count()
        logger.info("Total snapshots para desercion: %d", total)
        if total < 100:
            raise ValueError(f"Datos insuficientes: solo {total} registros")

        X, y = [], []
        for snapshot in snapshots:
            X.append(self._row_from_snapshot(snapshot, self.FEATURES))
            y.append(self._is_dropout(snapshot.enrollment))

        distribution = Counter(y)
        logger.info(
            "Distribucion target dropout: no=%d si=%d",
            distribution.get(0, 0),
            distribution.get(1, 0),
        )
        if len(distribution) < 2:
            raise ValueError(
                "Datos insuficientes: se requieren casos historicos con y sin desercion"
            )

        df = pd.DataFrame(X, columns=self.FEATURES).fillna(0)
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
        cv_auc = cross_val_score(model, df, y, cv=cv, scoring="roc_auc")
        cv_f1 = cross_val_score(model, df, y, cv=cv, scoring="f1")
        logger.info("CV ROC-AUC: %.4f (+/- %.4f)", cv_auc.mean(), cv_auc.std())
        logger.info("CV F1: %.4f (+/- %.4f)", cv_f1.mean(), cv_f1.std())

        model.fit(df, y)
        y_pred = model.predict(df)
        logger.info(
            "Classification report dropout (train):\n%s",
            classification_report(
                y,
                y_pred,
                labels=[0, 1],
                target_names=["continua", "deserta"],
                zero_division=0,
            ),
        )
        logger.info(
            "Confusion matrix dropout (train):\n%s",
            confusion_matrix(y, y_pred, labels=[0, 1]),
        )

        artifact = {
            "model": model,
            "features": self.FEATURES,
            "feature_importances": model.feature_importances_.tolist(),
            "model_type": "dropout_risk",
            "target": "student_dropout_next_period_or_year",
            "feature_labels": DROPOUT_FEATURE_LABELS,
            "training_params": params.__dict__,
            "training_metrics": {
                "cv_roc_auc_mean": float(cv_auc.mean()),
                "cv_roc_auc_std": float(cv_auc.std()),
                "cv_f1_mean": float(cv_f1.mean()),
                "cv_f1_std": float(cv_f1.std()),
                "target_distribution": {
                    "continua": distribution.get(0, 0),
                    "deserta": distribution.get(1, 0),
                },
            },
        }

        target_path = model_path or DROPOUT_MODEL_PATH
        joblib.dump(artifact, target_path)
        logger.info("Modelo de desercion guardado en: %s", target_path)
        return model

    @classmethod
    def predict(cls, enrollment_id, academic_period_id):
        from apps.analytics.student_risk.infrastructure.models import (
            StudentFeatureSnapshot,
        )

        snapshot = StudentFeatureSnapshot.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
        ).first()
        if not snapshot:
            return None

        raw = {col: _to_number(getattr(snapshot, col, 0)) for col in cls.FEATURES}
        return predict_dropout_from_features(raw)


def predict_dropout_from_features(raw_features: dict):
    import joblib

    if not DROPOUT_MODEL_PATH.exists():
        return None

    try:
        artifact = joblib.load(DROPOUT_MODEL_PATH)
    except Exception:
        logger.exception("No se pudo cargar el modelo de desercion")
        return None

    if artifact.get("model_type") != "dropout_risk":
        return None

    model = artifact["model"]
    features = artifact.get("features", TRAIN_DROPOUT_FEATURES)
    row = [_to_number(raw_features.get(col, 0)) for col in features]

    try:
        try:
            import pandas as pd

            X = pd.DataFrame([dict(zip(features, row))], columns=features)
        except ModuleNotFoundError:
            X = [row]

        proba = model.predict_proba(X)[0]
        classes = list(getattr(model, "classes_", [0, 1]))
        pos_idx = classes.index(1) if 1 in classes else len(classes) - 1
        probability = round(float(proba[pos_idx]) * 100, 2)
    except Exception:
        logger.exception("Error prediciendo desercion")
        return None

    importances = artifact.get("feature_importances", [])
    factors = [
        {
            "feature": features[i],
            "label": DROPOUT_FEATURE_LABELS.get(features[i], features[i]),
            "importance": round(float(importances[i]), 4) if i < len(importances) else 0,
            "value": float(raw_features.get(features[i], 0)),
        }
        for i in range(len(features))
    ]
    factors.sort(key=lambda item: item["importance"], reverse=True)

    return {
        "probability": probability,
        "risk_level": dropout_level(probability),
        "model_type": "dropout_risk",
        "factors": [factor for factor in factors if factor["importance"] > 0][:5],
    }
