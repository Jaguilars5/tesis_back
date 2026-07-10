"""
Entrenamiento del modelo por materia (modelo_riesgo_materia).

Predice la probabilidad de que una materia específica se vaya a rojo
(final_avg_truncated < 7.00) en un período académico.

Se entrena un RandomForest por materia (10 modelos independientes).

Ejecutar: python manage.py train_risk_model --subject-models
"""
import logging
from decimal import Decimal

from apps.analytics.student_risk.infrastructure.models import StudentFeatureSnapshot
from apps.grading.student_note.infrastructure.models import PeriodGradeSummary
from apps.attendance.attendance_core.infrastructure.models import Attendance
from .subject_features import (
    SUBJECT_FEATURES,
    TRAIN_SUBJECT_FEATURES,
    SUBJECT_CODES,
    subject_model_path,
    _to_number,
    SUBJECT_MODEL_DIR,
)

logger = logging.getLogger(__name__)


def _grade_trend(values):
    if len(values) < 2:
        return 0.0
    return float((values[-1] - values[0]) / Decimal(len(values) - 1))


class SubjectRiskModelTrainer:

    FEATURES = TRAIN_SUBJECT_FEATURES

    @staticmethod
    def _get_subject_attendance_rate(enrollment_id, subject_offering_id, academic_period_id):
        records = Attendance.objects.filter(
            enrollment_id=enrollment_id,
            teacher_subject_section__subject_offering_id=subject_offering_id,
            academic_period_id=academic_period_id,
        )
        total = records.count()
        if total == 0:
            return 0.0
        present = records.filter(attendance_status__code="P").count()
        return round(present / total * 100, 2)

    @staticmethod
    def _get_grade_trend_in_subject(enrollment_id, subject_offering_id, academic_period_id):
        from apps.grading.student_note.infrastructure.models import StudentNote
        notes = StudentNote.objects.filter(
            enrollment_id=enrollment_id,
            evaluative_activity__block_component__evaluation_block__academic_period_id=academic_period_id,
            evaluative_activity__teacher_subject_section__subject_offering_id=subject_offering_id,
        ).order_by("created_at")
        values = []
        for note in notes:
            if not note.manually_overridden:
                val = note.calculate_normalized_value()
                if val is not None:
                    values.append(val)
        return _grade_trend(values)

    @staticmethod
    def _get_subject_prev_period_grade(enrollment_id, subject_offering_id, academic_period_id):
        from apps.academic.academic_period.infrastructure.repositories import (
            AcademicPeriodRepository,
        )
        period = AcademicPeriodRepository.get_by_id(academic_period_id)
        if not period:
            return 0.0
        prev = type(period).objects.filter(
            school_year=period.school_year,
            start_date__lt=period.start_date,
        ).order_by("-start_date").first()
        if not prev:
            return 0.0
        summary = PeriodGradeSummary.objects.filter(
            enrollment_id=enrollment_id,
            subject_offering_id=subject_offering_id,
            academic_period=prev,
        ).first()
        return float(summary.final_avg_truncated) if summary else 0.0

    def _build_features(self, summary, snapshot):
        features = {}
        features["grade_in_subject"] = float(summary.final_avg_truncated)
        features["grade_trend_in_subject"] = self._get_grade_trend_in_subject(
            summary.enrollment_id, summary.subject_offering_id, summary.academic_period_id
        )
        features["attendance_in_subject"] = self._get_subject_attendance_rate(
            summary.enrollment_id, summary.subject_offering_id, summary.academic_period_id
        )
        features["formative_avg_in_subject"] = float(summary.formative_avg)
        features["summative_avg_in_subject"] = float(summary.summative_avg)
        features["prev_period_grade_in_subject"] = self._get_subject_prev_period_grade(
            summary.enrollment_id, summary.subject_offering_id, summary.academic_period_id
        )
        features["attendance_rate"] = _to_number(getattr(snapshot, "attendance_rate", 0))
        features["consecutive_absences_max"] = _to_number(getattr(snapshot, "consecutive_absences_max", 0))
        features["tardiness_count"] = _to_number(getattr(snapshot, "tardiness_count", 0))
        features["conduct_score"] = _to_number(getattr(snapshot, "conduct_score", 0))
        features["severe_incidents_count"] = _to_number(getattr(snapshot, "severe_incidents_count", 0))
        features["age_grade_gap"] = _to_number(getattr(snapshot, "age_grade_gap", 0))
        features["is_repeat"] = _to_number(getattr(snapshot, "is_repeat", False))
        features["has_special_needs"] = _to_number(getattr(snapshot, "has_special_needs", False))
        return features

    def train_subject(self, subject_code, model_path=None):
        import joblib
        import pandas as pd
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score, StratifiedKFold
        from sklearn.metrics import classification_report

        summaries = PeriodGradeSummary.objects.filter(
            subject_offering__subject_academic_config__subject__code=subject_code,
        ).select_related("enrollment", "subject_offering", "academic_period")

        total = summaries.count()
        logger.info("Materia %s: %s period summaries encontrados", subject_code, total)
        if total < 30:
            logger.warning("Materia %s: datos insuficientes (%s), se omite", subject_code, total)
            return None

        X, y = [], []
        skipped = 0
        for summary in summaries:
            snapshot = StudentFeatureSnapshot.objects.filter(
                enrollment_id=summary.enrollment_id,
                academic_period_id=summary.academic_period_id,
            ).first()
            if not snapshot:
                skipped += 1
                continue
            features = self._build_features(summary, snapshot)
            row = [_to_number(features.get(col, 0)) for col in self.FEATURES]
            X.append(row)
            y.append(1 if summary.is_failing else 0)

        if skipped:
            logger.info("Materia %s: %s registros omitidos (sin snapshot)", subject_code, skipped)

        logger.info(
            "Materia %s: pares (X, y) generados: %d (target=1: %d, target=0: %d)",
            subject_code, len(X), sum(y), len(X) - sum(y),
        )

        if len(X) < 50:
            logger.warning("Materia %s: datos insuficientes (%s), se omite", subject_code, len(X))
            return None

        df = pd.DataFrame(X, columns=self.FEATURES).fillna(0)

        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )

        try:
            cv = StratifiedKFold(n_splits=min(5, sum(y)), shuffle=True, random_state=42)
            cv_scores = cross_val_score(model, df, y, cv=cv, scoring="roc_auc")
            logger.info(
                "Materia %s: CV ROC-AUC: %.4f (±%.4f)",
                subject_code, cv_scores.mean(), cv_scores.std(),
            )
        except Exception as e:
            logger.warning("Materia %s: CV falló (%s), entrenando sin CV", subject_code, e)

        model.fit(df, y)

        y_pred = model.predict(df)
        logger.info(
            "Materia %s: classification report (train):\n%s",
            subject_code,
            classification_report(y, y_pred, target_names=["aprobado", "reprobado"]),
        )

        importance_df = pd.DataFrame({
            "feature": self.FEATURES,
            "importance": model.feature_importances_,
        }).sort_values("importance", ascending=False)
        logger.info("Materia %s: feature importances:\n%s", subject_code, importance_df)

        artifact = {
            "model": model,
            "features": self.FEATURES,
            "feature_importances": model.feature_importances_.tolist(),
            "subject_code": subject_code,
        }

        target_path = model_path or subject_model_path(subject_code)
        joblib.dump(artifact, target_path)
        logger.info("Materia %s: modelo guardado en: %s", subject_code, target_path)
        return model

    def train_all_subjects(self):
        results = {}
        for code in SUBJECT_CODES:
            logger.info("=" * 60)
            logger.info("Entrenando modelo para materia: %s", code)
            logger.info("=" * 60)
            model = self.train_subject(code)
            results[code] = model is not None
        trained = [code for code, ok in results.items() if ok]
        skipped = [code for code, ok in results.items() if not ok]
        logger.info("Modelos por materia entrenados: %s", trained)
        if skipped:
            logger.warning("Materias omitidas (datos insuficientes): %s", skipped)
        return results

    @classmethod
    def predict(cls, enrollment_id, subject_code, academic_period_id):
        """Predice la probabilidad de que una materia específica se vaya a rojo.

        Args:
            enrollment_id: ID de la matrícula
            subject_code: Código de la materia (MAT, FIS, ...)
            academic_period_id: ID del período académico

        Returns:
            Dict con probability (0-100) y risk_level (bajo, medio, alto)
            o None si no hay modelo entrenado.
        """
        import joblib

        path = subject_model_path(subject_code)
        if not path.exists():
            logger.warning("Modelo para %s no encontrado en %s", subject_code, path)
            return None

        try:
            artifact = joblib.load(path)
            model = artifact["model"]
            features_list = artifact["features"]
        except Exception as e:
            logger.error("Error cargando modelo %s: %s", subject_code, e)
            return None

        from apps.academic.subject_offering.infrastructure.repositories import (
            SubjectOfferingRepository,
        )
        from apps.grading.student_note.infrastructure.models import PeriodGradeSummary

        summary = PeriodGradeSummary.objects.filter(
            enrollment_id=enrollment_id,
            subject_offering__subject_academic_config__subject__code=subject_code,
            academic_period_id=academic_period_id,
        ).first()

        if not summary:
            return None

        snapshot = StudentFeatureSnapshot.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
        ).first()

        if not snapshot:
            return None

        trainer = cls()
        raw = trainer._build_features(summary, snapshot)
        features = [_to_number(raw.get(col, 0)) for col in features_list]

        import numpy as np
        proba = model.predict_proba([features])[0]
        prob_positive = float(proba[1]) if model.classes_[1] == 1 else float(proba[0])

        if prob_positive < 0.3:
            risk_level = "bajo"
        elif prob_positive < 0.6:
            risk_level = "medio"
        else:
            risk_level = "alto"

        return {
            "subject_code": subject_code,
            "probability": round(prob_positive * 100, 2),
            "risk_level": risk_level,
        }
