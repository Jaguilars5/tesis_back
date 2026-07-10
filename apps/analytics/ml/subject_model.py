"""
Entrenamiento del modelo de riesgo por materia (modelo único).

Predice la probabilidad de que UNA materia específica se vaya a rojo
(final_avg_truncated < 7.00) en un período académico.

Un solo RandomForest entrenado con todas las materias, usando
subject_code_idx (0-9) como feature para diferenciar patrones.

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
    SUBJECT_CODE_MAP,
    SUBJECT_MODEL_PATH,
    _to_number,
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
        subject_code = summary.subject_offering.subject_academic_config.subject.code
        features = {}
        features["subject_code_idx"] = SUBJECT_CODE_MAP.get(subject_code, 0)
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

    def train(self, model_path=None):
        import joblib
        import pandas as pd
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score, StratifiedKFold
        from sklearn.metrics import classification_report

        summaries = PeriodGradeSummary.objects.filter(
            subject_offering__subject_academic_config__subject__code__in=list(SUBJECT_CODE_MAP.keys()),
        ).select_related(
            "enrollment",
            "subject_offering__subject_academic_config__subject",
            "academic_period",
        )

        total = summaries.count()
        logger.info("Total period summaries (todas las materias): %d", total)
        if total < 100:
            raise ValueError(f"Datos insuficientes: solo {total} registros")

        X, y = [], []
        skipped = 0
        # Prefetch todos los snapshots en un dict para evitar N+1 queries
        summary_ids = list(summaries.values_list("enrollment_id", "academic_period_id"))
        enrollment_ids = list(set(s[0] for s in summary_ids))
        period_ids = list(set(s[1] for s in summary_ids))

        snapshots_qs = StudentFeatureSnapshot.objects.filter(
            enrollment_id__in=enrollment_ids,
            academic_period_id__in=period_ids,
        ).only("id", "enrollment_id", "academic_period_id",
               "attendance_rate", "consecutive_absences_max", "tardiness_count",
               "conduct_score", "severe_incidents_count",
               "age_grade_gap", "is_repeat", "has_special_needs")

        snapshot_map = {}
        for snap in snapshots_qs:
            snapshot_map[(snap.enrollment_id, snap.academic_period_id)] = snap

        batch_size = 500
        processed = 0
        for summary in summaries.iterator(chunk_size=batch_size):
            key = (summary.enrollment_id, summary.academic_period_id)
            snapshot = snapshot_map.get(key)
            if not snapshot:
                skipped += 1
                continue
            features = self._build_features(summary, snapshot)
            row = [_to_number(features.get(col, 0)) for col in self.FEATURES]
            X.append(row)
            y.append(1 if summary.is_failing else 0)
            processed += 1
            if processed % 5000 == 0:
                logger.info("Procesados %d / %d registros...", processed, total)

        if skipped:
            logger.info("Registros omitidos (sin snapshot): %d", skipped)

        logger.info(
            "Pares (X, y) generados: %d (target=1: %d, target=0: %d)",
            len(X), sum(y), len(X) - sum(y),
        )

        if len(X) < 100:
            raise ValueError(f"Datos insuficientes: solo {len(X)} registros")

        df = pd.DataFrame(X, columns=self.FEATURES).fillna(0)

        logger.info("Estadísticas descriptivas:\n%s", df.describe())

        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )

        try:
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            cv_scores = cross_val_score(model, df, y, cv=cv, scoring="roc_auc")
            logger.info("CV ROC-AUC: %.4f (±%.4f)", cv_scores.mean(), cv_scores.std())
        except Exception as e:
            logger.warning("CV falló (%s), entrenando sin CV", e)

        model.fit(df, y)

        y_pred = model.predict(df)
        logger.info(
            "Classification report (train):\n%s",
            classification_report(y, y_pred, target_names=["aprobado", "reprobado"]),
        )

        importance_df = pd.DataFrame({
            "feature": self.FEATURES,
            "importance": model.feature_importances_,
        }).sort_values("importance", ascending=False)
        logger.info("Feature importances:\n%s", importance_df)

        artifact = {
            "model": model,
            "features": self.FEATURES,
            "feature_importances": model.feature_importances_.tolist(),
            "model_type": "subject_risk",
        }

        target_path = model_path or SUBJECT_MODEL_PATH
        joblib.dump(artifact, target_path)
        logger.info("Modelo guardado en: %s", target_path)
        return model

    @classmethod
    def predict(cls, enrollment_id, subject_code, academic_period_id):
        import joblib
        import numpy as np

        if not SUBJECT_MODEL_PATH.exists():
            logger.warning("Modelo no encontrado en %s", SUBJECT_MODEL_PATH)
            return None

        try:
            artifact = joblib.load(SUBJECT_MODEL_PATH)
            model = artifact["model"]
            features_list = artifact["features"]
        except Exception as e:
            logger.error("Error cargando modelo: %s", e)
            return None

        from apps.grading.student_note.infrastructure.models import PeriodGradeSummary

        summary = PeriodGradeSummary.objects.filter(
            enrollment_id=enrollment_id,
            subject_offering__subject_academic_config__subject__code=subject_code,
            academic_period_id=academic_period_id,
        ).select_related("subject_offering__subject_academic_config__subject").first()

        if not summary:
            logger.warning("No hay period summary para enrollment=%s subject=%s period=%s",
                           enrollment_id, subject_code, academic_period_id)
            return None

        snapshot = StudentFeatureSnapshot.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
        ).first()

        if not snapshot:
            logger.warning("No hay snapshot para enrollment=%s period=%s",
                           enrollment_id, academic_period_id)
            return None

        trainer = cls()
        raw = trainer._build_features(summary, snapshot)
        features = [_to_number(raw.get(col, 0)) for col in features_list]

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
