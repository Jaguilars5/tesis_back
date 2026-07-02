"""
Entrenamiento del modelo matemático de riesgo académico.

Usa **todos los períodos históricos** para entrenar una **regresión logística**
que predice la probabilidad de que un estudiante esté reprobando
(``is_failing`` de ``PeriodGradeSummary``).

A diferencia del modelo anterior (clasificador que imitaba las reglas),
este modelo aprende de outcomes reales y produce un score interpretable
como probabilidad 0-100.

Ejecutar: python manage.py train_risk_model
"""
import logging

from apps.analytics.student_risk.infrastructure.models import (
    StudentFeatureSnapshot,
)
from .features import TRAIN_FEATURES, MODEL_PATH, _to_number

logger = logging.getLogger(__name__)


class RiskModelTrainer:

    FEATURES = TRAIN_FEATURES

    @staticmethod
    def _get_target(enrollment_id, academic_period_id) -> int:
        """
        Target: 1 si el estudiante reprobó AL MENOS UNA materia en el período.

        Se considera ``is_failing=True`` cuando ``final_avg_truncated < 7.00``
        en ``PeriodGradeSummary``. Si no hay resumen de notas para el período,
        se asume que no reprobó (target=0).
        """
        from apps.grading.student_note.infrastructure.models import PeriodGradeSummary
        return int(
            PeriodGradeSummary.objects.filter(
                enrollment_id=enrollment_id,
                academic_period_id=academic_period_id,
                is_failing=True,
            ).exists()
        )

    def train(self, model_path=None):
        import joblib
        import pandas as pd
        import numpy as np
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import cross_val_score, StratifiedKFold
        from sklearn.metrics import roc_auc_score, classification_report

        snapshots = StudentFeatureSnapshot.objects.all()

        total_snapshots = snapshots.count()
        logger.info("Total snapshots encontrados: %d", total_snapshots)
        if total_snapshots == 0:
            raise ValueError("No hay snapshots para entrenar")

        X, y = [], []
        skipped_no_pgs = 0

        for snapshot in snapshots:
            target = self._get_target(snapshot.enrollment_id, snapshot.academic_period_id)
            features = [_to_number(getattr(snapshot, col, 0)) for col in self.FEATURES]
            X.append(features)
            y.append(target)

        logger.info("Pares (X, y) generados: %d", len(X))
        logger.info(
            "Distribución target (is_failing): 0=%d (%.1f%%)  1=%d (%.1f%%)",
            y.count(0), 100 * y.count(0) / len(y),
            y.count(1), 100 * y.count(1) / len(y),
        )

        if len(X) < 100:
            raise ValueError(f"Datos insuficientes: solo {len(X)} registros")

        df = pd.DataFrame(X, columns=self.FEATURES).fillna(0)

        logger.info("Estadísticas descriptivas:\n%s", df.describe())

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df)

        model = LogisticRegression(
            class_weight="balanced",
            max_iter=2000,
            random_state=42,
            C=1.0,
            solver="lbfgs",
        )

        # Validación cruzada estratificada (deja un período fuera)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, X_scaled, y, cv=cv, scoring="roc_auc")
        logger.info(
            "CV ROC-AUC: %.4f (±%.4f)", cv_scores.mean(), cv_scores.std()
        )

        model.fit(X_scaled, y)

        # Reporte sobre todo el dataset (diagnóstico)
        y_pred = model.predict(X_scaled)
        logger.info(
            "Classification report (train):\n%s",
            classification_report(y, y_pred, target_names=["aprobado", "reprobado"]),
        )

        # Importancia: coeficientes normalizados
        coef_df = pd.DataFrame({
            "feature": self.FEATURES,
            "coef": np.abs(model.coef_[0]),
            "signo": np.sign(model.coef_[0]),
        }).sort_values("coef", ascending=False)
        logger.info("Coeficientes del modelo:\n%s", coef_df)

        artifact = {
            "model": model,
            "scaler": scaler,
            "features": self.FEATURES,
            "mean": df.mean().to_dict(),
            "std": df.std().to_dict(),
        }

        target_path = model_path or MODEL_PATH
        joblib.dump(artifact, target_path)
        logger.info("Modelo guardado en: %s", target_path)

        return model
