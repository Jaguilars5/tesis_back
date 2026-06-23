"""
Script para entrenar el modelo de riesgo académico.
Ejecutar con: python manage.py train_risk_model --period-id=X

El contrato de features (nombres y orden de columnas) vive en `features.py` y es
compartido con la inferencia (`apps/analytics/tasks`). NO duplicar la lista aquí.
"""
from ..models import StudentFeatureSnapshot, StudentRiskScore
from .features import FEATURE_COLUMNS, MODEL_PATH, _to_number


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

        X = []
        y = []

        for snapshot in snapshots:
            score = StudentRiskScore.objects.filter(
                enrollment=snapshot.enrollment,
                academic_period=snapshot.academic_period,
            ).first()
            if not score:
                continue

            features = [_to_number(getattr(snapshot, col, 0)) for col in self.FEATURE_COLUMNS]
            X.append(features)
            y.append(score.risk_label)

        if len(X) < 10:
            raise ValueError("Datos insuficientes para entrenar")

        df = pd.DataFrame(X, columns=self.FEATURE_COLUMNS)
        df = df.fillna(0)
        X_train, X_test, y_train, y_test = train_test_split(
            df, y, test_size=0.2, stratify=y, random_state=42
        )

        model = GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        print(classification_report(y_test, y_pred))

        target_path = model_path or MODEL_PATH
        joblib.dump(model, target_path)
        print(f"Modelo guardado en: {target_path}")

        return model
