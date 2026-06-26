"""
Fase 3 — Limpieza de features muertas (PLAN_IMPLEMENTACION.md §6.2, §6.5).

Verifica que:
- §6.2: `feature_builder` ya no emite las features fijas `tareas_entregadas` /
  `tareas_pendientes` (ruido constante en 0).
- §6.5: no quedan campos "huérfanos" en `StudentFeatureSnapshot`, es decir, todo
  campo persistido (no metadato) pertenece al contrato canónico `FEATURE_COLUMNS`
  (se usa en entrenamiento y/o inferencia).
"""

from django.test import SimpleTestCase

from apps.analytics.ml import features
from apps.analytics.student_risk.infrastructure.models import StudentFeatureSnapshot
from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder


# Campos del snapshot que son metadatos / relaciones, NO features del modelo.
METADATA_FIELDS = {
    "id",
    "enrollment",
    "academic_period",
    "is_current",
    "snapshot_trigger",
    "calculated_at",
    "created_at",
    "updated_at",
}

# Dimensiones analíticas/segmentación persistidas para dashboards y reportes,
# que deliberadamente NO son features numéricas del modelo (Fase 4 §5 F).
ANALYTICAL_DIMENSION_FIELDS = {
    "city",
    "special_needs_type",
    "withdrawal_reason",
}


class Phase3DeadFeatureKeysTest(SimpleTestCase):
    def test_build_grades_drops_dead_task_features(self):
        builder = AcademicRiskFeatureBuilder(student_id=1, academic_period_id=1)
        grades = builder._build_grades([])

        self.assertNotIn("tareas_entregadas", grades)
        self.assertNotIn("tareas_pendientes", grades)
        # Las features vivas siguen presentes.
        self.assertIn("promedio_actual", grades)
        self.assertIn("materias_reprobadas", grades)


class Phase3NoOrphanColumnsTest(SimpleTestCase):
    def _feature_columns_in_model(self):
        return {
            field.name
            for field in StudentFeatureSnapshot._meta.fields
            if field.name not in METADATA_FIELDS
            and field.name not in ANALYTICAL_DIMENSION_FIELDS
        }

    def test_every_persisted_column_is_a_model_feature(self):
        persisted = self._feature_columns_in_model()
        # Todo campo persistido (que no sea metadato ni dimensión analítica) debe
        # estar en el contrato de features (usado en entrenamiento/inferencia).
        orphan = persisted - set(features.FEATURE_COLUMNS)
        self.assertEqual(
            orphan,
            set(),
            f"Columnas persistidas sin uso en entrenamiento/inferencia: {orphan}",
        )

    def test_feature_contract_matches_persisted_columns(self):
        persisted = self._feature_columns_in_model()
        # Y todo feature del contrato debe existir como columna persistida.
        self.assertEqual(persisted, set(features.FEATURE_COLUMNS))

    def test_active_alerts_column_removed(self):
        field_names = {f.name for f in StudentFeatureSnapshot._meta.fields}
        self.assertNotIn("active_alerts", field_names)
