"""
Script para entrenar el modelo de riesgo académico.
Ejecutar con: python manage.py train_risk_model --period-id=X
"""
import joblib
import pandas as pd
from pathlib import Path
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from ..models import StudentFeatureSnapshot, StudentRiskScore


class RiskModelTrainer:

    FEATURE_COLUMNS = [
        "attendance_rate",
        "consecutive_absences_max",
        "tardiness_count",
        "justified_absences",
        "unjustified_absences",
        "formative_avg_normalized",
        "summative_avg_normalized",
        "grade_trend_slope",
        "failing_subjects_count",
        "conduct_score",
        "severe_incidents_count",
        "family_notified_ratio",
        "prev_period_avg_grade",
        "age_grade_gap",
        "is_repeat",
        "has_special_needs",
    ]

    def train(self, period_id=None):
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

            features = [getattr(snapshot, col, 0) or 0 for col in self.FEATURE_COLUMNS]
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

        model_path = Path(__file__).parent / "risk_model.joblib"
        joblib.dump(model, model_path)
        print(f"Modelo guardado en: {model_path}")

        return model
