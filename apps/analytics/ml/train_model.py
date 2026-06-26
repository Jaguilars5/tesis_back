"""
Script para entrenar el modelo de riesgo académico.
Ejecutar con: python manage.py train_risk_model --period-id=X

El contrato de features (nombres y orden de columnas) vive en `features.py` y es
compartido con la inferencia (`apps/analytics/tasks`). NO duplicar la lista aquí.
"""
import logging

from apps.analytics.student_risk.infrastructure.models import (
    StudentFeatureSnapshot,
    StudentRiskScore,
)
from .features import FEATURE_COLUMNS, MODEL_PATH, _to_number

logger = logging.getLogger(__name__)


class RiskModelTrainer:

    # Fuente de verdad única: el mismo contrato que consume la inferencia.
    FEATURE_COLUMNS = FEATURE_COLUMNS

    def train(self, period_id=None, model_path=None):
        # Imports perezosos: joblib/pandas/scikit-learn solo se requieren al
        # entrenar (no para importar el contrato de features ni la clase).
        import joblib
        import pandas as pd
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report

        snapshots = StudentFeatureSnapshot.objects.all()
        if period_id:
            snapshots = snapshots.filter(academic_period_id=period_id)

        total_snapshots = snapshots.count()
        logger.info("Total snapshots encontrados: %d", total_snapshots)
        if total_snapshots == 0:
            raise ValueError("No hay snapshots para entrenar")

        X = []
        y = []
        skipped_no_score = 0

        for snapshot in snapshots:
            score = StudentRiskScore.objects.filter(
                enrollment=snapshot.enrollment,
                academic_period=snapshot.academic_period,
            ).first()
            if not score:
                skipped_no_score += 1
                continue

            features = [_to_number(getattr(snapshot, col, 0)) for col in self.FEATURE_COLUMNS]
            X.append(features)
            y.append(score.risk_label)

        logger.info(
            "Snapshots sin StudentRiskScore (skipped): %d", skipped_no_score
        )
        logger.info("Pares (X, y) generados: %d", len(X))

        if len(X) < 10:
            raise ValueError("Datos insuficientes para entrenar")

        df = pd.DataFrame(X, columns=self.FEATURE_COLUMNS)
        df = df.fillna(0)

        from collections import Counter
        label_dist = Counter(y)
        logger.info("Distribución de risk_label: %s", dict(label_dist))

        pd.set_option("display.max_columns", 20)
        pd.set_option("display.width", 200)
        pd.set_option("display.float_format", lambda v: "%.4f" % v)
        logger.info("Estadísticas descriptivas de features:\n%s", df.describe())

        num_zeros = (df == 0).sum().sum()
        total_cells = df.shape[0] * df.shape[1]
        logger.info(
            "Celdas con valor 0: %d de %d (%.1f%%)",
            num_zeros, total_cells, 100 * num_zeros / total_cells,
        )

        X_train, X_test, y_train, y_test = train_test_split(
            df, y, test_size=0.2, stratify=y, random_state=42
        )

        logger.info("Train size: %d | Test size: %d", len(X_train), len(X_test))
        logger.info(
            "Distribución train: %s",
            dict(Counter(y_train)),
        )
        logger.info(
            "Distribución test: %s",
            dict(Counter(y_test)),
        )

        model = GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred)
        logger.info("Classification report:\n%s", report)

        target_path = model_path or MODEL_PATH
        joblib.dump(model, target_path)
        logger.info("Modelo guardado en: %s", target_path)

        return model
