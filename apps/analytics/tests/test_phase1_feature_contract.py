"""
Fase 1 — Contrato único de features tren/inferencia (PLAN_IMPLEMENTACION.md §6.1, §6.5).

Verifica que:
- `FEATURE_COLUMNS` (entrenamiento) y la inferencia compartan EXACTAMENTE las
  mismas columnas, nombres y orden (test que falla si divergen).
- Con un modelo entrenado presente y columnas coincidentes, `_predict_ml_score`
  retorna un score SIN caer a fallback.
- Ante un desajuste de columnas, se cae a fallback de forma INTENCIONAL (None),
  no por excepción silenciosa.
- Los campos §6.5 (is_repeat, age_grade_gap, prev_period_avg_grade,
  family_notified_ratio, consecutive_absences_max, has_special_needs) están en el
  contrato y fluyen a la inferencia.
"""

import importlib.util
import os
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from apps.analytics.ml import features
from apps.analytics.ml.features import FEATURE_COLUMNS, TRAIN_FEATURES
from apps.analytics.ml.train_model import RiskModelTrainer
from apps.analytics import tasks
from apps.analytics.student_risk.domain import risk_engine


def _has(module_name):
    return importlib.util.find_spec(module_name) is not None


HAS_JOBLIB = _has("joblib")
HAS_SKLEARN = _has("sklearn")
HAS_PANDAS = _has("pandas")


INERT_FIELDS_6_5 = [
    "is_repeat",
    "age_grade_gap",
    "prev_period_avg_grade",
    "family_notified_ratio",
    "consecutive_absences_max",
    "has_special_needs",
]


# Modelos falsos a nivel de módulo para que joblib.dump pueda picklearlos.
class FakeProbaModel:
    """Imita un clasificador multiclase institucional con predict_proba."""

    def __init__(self, columns, classes=(0, 1, 2), probs=(0.1, 0.2, 0.7)):
        self.feature_names_in_ = list(columns)
        self.classes_ = list(classes)
        self._probs = list(probs)

    def predict_proba(self, X):
        return [self._probs]

    def predict(self, X):
        return [self.classes_[self._probs.index(max(self._probs))]]


def _sample_snapshot():
    return {
        "estudiante_id": "1",
        "periodo": "1",
        "variables": {
            "conducta": {
                "faltas_leves": 2,
                "faltas_moderadas": 1,
                "faltas_graves": 3,
                "ratio_notificacion_familiar": 0.5,
            },
            "asistencia": {
                "porcentaje_asistencia": 72.0,
                "total_faltas": 6,
                "faltas_justificadas": 2,
                "faltas_injustificadas": 4,
                "tardanzas": 1,
                "total_registros": 20,
                "max_faltas_consecutivas": 3,
            },
            "calificaciones": {
                "promedio_actual": 6.5,
                "materias_reprobadas": 2,
                "ultimo_examen": 6.0,
                "tendencia_notas": -0.2,
                "total_calificaciones": 5,
            },
        },
    }


class Phase1ColumnContractTest(SimpleTestCase):
    """El test que debe FALLAR si tren e inferencia divergen."""

    def test_trainer_uses_canonical_columns(self):
        self.assertEqual(RiskModelTrainer.FEATURES, TRAIN_FEATURES)

    def test_contract_has_16_columns(self):
        self.assertEqual(len(FEATURE_COLUMNS), 16)
        self.assertEqual(len(set(FEATURE_COLUMNS)), 16, "No debe haber columnas duplicadas")

    def test_inference_from_snapshot_emits_exact_columns_in_order(self):
        feature_dict = features.feature_dict_from_snapshot(_sample_snapshot())
        self.assertEqual(list(feature_dict.keys()), FEATURE_COLUMNS)

    def test_inference_from_metrics_emits_exact_columns_in_order(self):
        metrics = {
            "attendance_rate": Decimal("72.00"),
            "consecutive_absences_max": 3,
            "tardiness_count": 1,
            "justified_absences": 2,
            "unjustified_absences": 4,
            "avg_grade_normalized": Decimal("6.50"),
            "grade_trend_slope": Decimal("-0.20"),
            "failing_subjects_count": 2,
            "conduct_score": Decimal("6.00"),
            "severe_incidents_count": 3,
            "family_notified_ratio": Decimal("0.50"),
            "prev_period_avg_grade": Decimal("7.10"),
            "age_grade_gap": 1,
            "is_repeat": True,
            "has_special_needs": False,
        }
        feature_dict = features.feature_dict_from_metrics(metrics)
        self.assertEqual(list(feature_dict.keys()), FEATURE_COLUMNS)
        # avg_grade_normalized debe replicarse a formativo y sumativo
        self.assertEqual(feature_dict["formative_avg_normalized"], 6.5)
        self.assertEqual(feature_dict["summative_avg_normalized"], 6.5)
        # booleanos -> 1.0/0.0
        self.assertEqual(feature_dict["is_repeat"], 1.0)
        self.assertEqual(feature_dict["has_special_needs"], 0.0)

    def test_feature_vector_helper_matches_contract(self):
        snapshot = _sample_snapshot()
        self.assertEqual(list(tasks._feature_vector(snapshot).keys()), FEATURE_COLUMNS)
        self.assertEqual(
            list(tasks._feature_vector(snapshot, {"is_repeat": True}).keys()),
            FEATURE_COLUMNS,
        )

    def test_all_values_are_numeric(self):
        feature_dict = features.feature_dict_from_snapshot(_sample_snapshot())
        for col, value in feature_dict.items():
            self.assertIsInstance(value, float, f"{col} debe ser numérico para sklearn")


class Phase1InertFieldsTest(SimpleTestCase):
    """§6.5 — los campos antes inertes ahora están en el contrato y fluyen."""

    def test_inert_fields_are_in_contract(self):
        for field in INERT_FIELDS_6_5:
            self.assertIn(field, FEATURE_COLUMNS)

    def test_db_derived_fields_flow_from_metrics(self):
        snapshot = _sample_snapshot()
        metrics = {
            "prev_period_avg_grade": Decimal("8.00"),
            "age_grade_gap": 2,
            "is_repeat": True,
            "has_special_needs": True,
        }
        feature_dict = features.feature_dict_from_snapshot(snapshot, metrics)
        self.assertEqual(feature_dict["prev_period_avg_grade"], 8.0)
        self.assertEqual(feature_dict["age_grade_gap"], 2.0)
        self.assertEqual(feature_dict["is_repeat"], 1.0)
        self.assertEqual(feature_dict["has_special_needs"], 1.0)

    def test_attendance_and_family_fields_flow_from_snapshot(self):
        feature_dict = features.feature_dict_from_snapshot(_sample_snapshot())
        self.assertEqual(feature_dict["consecutive_absences_max"], 3.0)
        self.assertEqual(feature_dict["family_notified_ratio"], 0.5)
        self.assertEqual(feature_dict["justified_absences"], 2.0)
        self.assertEqual(feature_dict["unjustified_absences"], 4.0)
        self.assertEqual(feature_dict["severe_incidents_count"], 3.0)


class Phase1PredictionTest(SimpleTestCase):
    """Comportamiento de _predict_ml_score con/ sin modelo y con desajuste."""

    def setUp(self):
        self._tmp_files = []

    def tearDown(self):
        for path in self._tmp_files:
            try:
                os.remove(path)
            except OSError:
                pass

    def _dump_model(self, model, *, model_type="general_institutional_risk"):
        import joblib

        fd, path = tempfile.mkstemp(suffix=".joblib")
        os.close(fd)
        joblib.dump(
            {
                "model": model,
                "features": list(getattr(model, "feature_names_in_", FEATURE_COLUMNS)),
                "feature_importances": [1 / len(FEATURE_COLUMNS)] * len(FEATURE_COLUMNS),
                "model_type": model_type,
                "score_class_centers": {0: 20.0, 1: 55.0, 2: 85.0},
            },
            path,
        )
        self._tmp_files.append(path)
        from pathlib import Path

        return Path(path)

    def test_returns_none_when_model_absent(self):
        # MODEL_PATH real no existe; debe ser fallback intencional (None).
        self.assertIsNone(tasks._predict_ml_score(_sample_snapshot()))

    @unittest.skipUnless(HAS_JOBLIB, "joblib no instalado en este entorno")
    def test_returns_score_with_matching_model_no_fallback(self):
        model_path = self._dump_model(FakeProbaModel(FEATURE_COLUMNS))
        with patch.object(risk_engine, "MODEL_PATH", model_path):
            score = tasks._predict_ml_score(_sample_snapshot())
        self.assertIsNotNone(score, "Con columnas coincidentes NO debe caer a fallback")
        # 0.1*20 + 0.2*55 + 0.7*85 = 72.5, dentro del rango rojo.
        self.assertAlmostEqual(score, 72.5, places=2)

    @unittest.skipUnless(HAS_JOBLIB, "joblib no instalado en este entorno")
    def test_column_mismatch_falls_back_intentionally(self):
        model_path = self._dump_model(FakeProbaModel(["wrong_a", "wrong_b"]))
        with patch.object(risk_engine, "MODEL_PATH", model_path):
            with self.assertLogs(
                "apps.analytics.student_risk.domain.risk_engine", level="WARNING"
            ) as logs:
                score = tasks._predict_ml_score(_sample_snapshot())
        self.assertIsNone(score)
        self.assertTrue(
            any("FALLBACK-INTENCIONAL" in msg for msg in logs.output),
            "El desajuste debe loguearse como fallback intencional, no como error",
        )

    @unittest.skipUnless(
        HAS_JOBLIB and HAS_SKLEARN and HAS_PANDAS,
        "Requiere joblib + scikit-learn + pandas",
    )
    def test_real_gradient_boosting_scores_without_fallback(self):
        import pandas as pd
        from sklearn.ensemble import GradientBoostingClassifier

        rows, labels = [], []
        for i in range(40):
            high_risk = i % 2 == 0
            rows.append(
                {
                    "attendance_rate": 50.0 if high_risk else 95.0,
                    "consecutive_absences_max": 5 if high_risk else 0,
                    "tardiness_count": 4 if high_risk else 0,
                    "justified_absences": 1,
                    "unjustified_absences": 6 if high_risk else 0,
                    "formative_avg_normalized": 4.0 if high_risk else 9.0,
                    "summative_avg_normalized": 4.0 if high_risk else 9.0,
                    "grade_trend_slope": -0.5 if high_risk else 0.2,
                    "failing_subjects_count": 3 if high_risk else 0,
                    "conduct_score": 3.0 if high_risk else 9.5,
                    "severe_incidents_count": 4 if high_risk else 0,
                    "family_notified_ratio": 0.8 if high_risk else 0.0,
                    "prev_period_avg_grade": 4.5 if high_risk else 8.5,
                    "age_grade_gap": 2 if high_risk else 0,
                    "is_repeat": 1.0 if high_risk else 0.0,
                    "has_special_needs": 0.0,
                }
            )
            labels.append(2 if high_risk else 0)

        df = pd.DataFrame(rows, columns=FEATURE_COLUMNS)
        model = GradientBoostingClassifier(random_state=42).fit(df, labels)
        model_path = self._dump_model(model)

        with patch.object(risk_engine, "MODEL_PATH", model_path):
            score = tasks._predict_ml_score(_sample_snapshot())

        self.assertIsNotNone(score)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)


class Phase1PersistenceMetricsTest(TestCase):
    """build_persistence_metrics ahora completa los campos antes constantes en 0."""

    def setUp(self):
        from apps.institutions.models import (
            AcademicGrade,
            AcademicLevel,
            AcademicSublevel,
            SchoolYear,
            Section,
        )
        from apps.academic.academic_period import AcademicPeriod
        from apps.students.models import Enrollment
        from apps.core.tests.helpers import create_test_student

        self.school_year = SchoolYear.objects.create(
            start_date=date(2026, 1, 1), end_date=date(2026, 12, 31)
        )
        self.period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            name="P1",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
        )
        level = AcademicLevel.objects.create(name="Basica")
        sublevel = AcademicSublevel.objects.create(academic_level=level, name="Básica")
        grade = AcademicGrade.objects.create(academic_sublevel=sublevel, name="8")
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=grade,
            parallel="A",
            capacity=30,
        )
        self.student = create_test_student(
            document_number="0912345678",
            names="Juan",
            last_names="Lopez",
            birth_date=date(2012, 1, 1),
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            section=self.section,
            enrollment_status="ACT",
        )

    def test_metrics_include_previously_constant_fields(self):
        from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder

        builder = AcademicRiskFeatureBuilder(self.student.id, self.period.id)
        snapshot = builder.build()
        metrics = builder.build_persistence_metrics(snapshot)

        for key in ("justified_absences", "unjustified_absences", "severe_incidents_count"):
            self.assertIn(key, metrics)

    def test_metrics_map_cleanly_to_feature_contract(self):
        from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder

        builder = AcademicRiskFeatureBuilder(self.student.id, self.period.id)
        snapshot = builder.build()
        metrics = builder.build_persistence_metrics(snapshot)

        feature_dict = features.feature_dict_from_metrics(metrics)
        self.assertEqual(list(feature_dict.keys()), FEATURE_COLUMNS)
