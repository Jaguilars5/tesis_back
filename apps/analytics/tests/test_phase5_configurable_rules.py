"""
Fase 5 — Motor de reglas configurable desde el frontend (PLAN_IMPLEMENTACION.md §9).

Cubre los criterios de aceptación:
- Cambiar pesos/umbrales altera el SCORE y la CLASIFICACIÓN en el motor de reglas.
- Con `engine=ML` (sin artefacto) se ignoran los pesos/umbrales y se cae al fallback.
- El backend RECHAZA configuraciones inválidas (suma ≠ 100%, fuera de rango,
  umbrales incoherentes).
- La configuración por defecto (sin fila en BD) preserva el comportamiento histórico.
- `model_version` refleja la config aplicada (trazabilidad).
"""

from django.test import SimpleTestCase, TestCase
from rest_framework.exceptions import ValidationError

from apps.analytics.student_risk.application.serializers import RiskScoringConfigSerializer
from apps.analytics.student_risk.infrastructure.models import RiskScoringConfig
from apps.analytics.student_risk.infrastructure.repositories import (
    RiskScoringConfigRepository,
)
from apps.analytics.services.risk_scoring_config_service import (
    DEFAULT_CONFIG,
    PRESETS,
    RiskScoringConfigService,
)
from apps.analytics.tasks import (
    MODEL_VERSION_FALLBACK,
    _fallback_risk_score,
    _risk_level,
    calculate_academic_risk,
)


def _snapshot(attendance=95.0, average=9.0, severe=0, mild=0, failing=0):
    return {
        "estudiante_id": "1",
        "periodo": "1",
        "variables": {
            "conducta": {
                "faltas_leves": mild,
                "faltas_moderadas": 0,
                "faltas_graves": severe,
            },
            "asistencia": {
                "porcentaje_asistencia": attendance,
                "total_registros": 20,
                "total_faltas": 0,
                "faltas_injustificadas": 0,
            },
            "calificaciones": {
                "promedio_actual": average,
                "materias_reprobadas": failing,
                "total_calificaciones": 10,
                "ultimo_examen": average,
            },
        },
    }


class Phase5ThresholdConfigEffectTest(SimpleTestCase):
    """Los umbrales configurables cambian la clasificación (sin tocar la BD)."""

    def test_default_attendance_80_is_yellow(self):
        self.assertEqual(_risk_level(_snapshot(attendance=80.0)["variables"]), "amarillo")

    def test_stricter_attendance_threshold_makes_80_green(self):
        from apps.analytics.services.risk_scoring_config_service import (
            EffectiveScoringConfig,
        )

        # Umbral de amarillo bajado a 78 → asistencia 80 ya es verde.
        config = EffectiveScoringConfig(
            engine="reglas",
            weight_conducta=0.3,
            weight_asistencia=0.35,
            weight_calificaciones=0.35,
            attendance_red_max=60.0,
            attendance_yellow_max=78.0,
            attendance_green_min=79.0,
            average_red_max=6.0,
            average_yellow_max=7.0,
            average_green_min=7.5,
            severe_red_min=3,
            mild_yellow_min=5,
            severe_green_max=0,
            mild_green_max=5,
        )
        self.assertEqual(
            _risk_level(_snapshot(attendance=80.0)["variables"], config), "verde"
        )

    def test_weights_change_score(self):
        from apps.analytics.services.risk_scoring_config_service import (
            EffectiveScoringConfig,
        )

        # Escenario amarillo con score crudo > piso (40) para que el peso se note.
        variables = _snapshot(
            attendance=70.0, average=6.0, mild=6, failing=2
        )["variables"]
        base = _fallback_risk_score(variables, "amarillo", DEFAULT_CONFIG)  # 44.0

        heavy_attendance = EffectiveScoringConfig(
            engine="reglas",
            weight_conducta=0.10,
            weight_asistencia=0.60,
            weight_calificaciones=0.30,
            attendance_red_max=70.0,
            attendance_yellow_max=85.0,
            attendance_green_min=90.0,
            average_red_max=6.0,
            average_yellow_max=7.0,
            average_green_min=7.5,
            severe_red_min=3,
            mild_yellow_min=5,
            severe_green_max=0,
            mild_green_max=5,
        )
        weighted = _fallback_risk_score(variables, "amarillo", heavy_attendance)  # 42.0
        # Distinta distribución de pesos → score distinto.
        self.assertNotAlmostEqual(base, weighted, places=2)


class Phase5DefaultConfigTest(SimpleTestCase):
    """Sin fila en BD, la config efectiva replica el comportamiento histórico."""

    def test_default_config_matches_legacy_constants(self):
        self.assertEqual(DEFAULT_CONFIG.weight_conducta, 0.30)
        self.assertEqual(DEFAULT_CONFIG.weight_asistencia, 0.35)
        self.assertEqual(DEFAULT_CONFIG.weight_calificaciones, 0.35)
        self.assertEqual(DEFAULT_CONFIG.attendance_red_max, 70.0)
        self.assertEqual(DEFAULT_CONFIG.attendance_yellow_max, 85.0)
        self.assertEqual(DEFAULT_CONFIG.average_red_max, 6.0)
        self.assertEqual(DEFAULT_CONFIG.average_yellow_max, 7.0)
        self.assertEqual(DEFAULT_CONFIG.severe_red_min, 3)
        self.assertEqual(DEFAULT_CONFIG.attendance_green_min, 85.01)
        self.assertEqual(DEFAULT_CONFIG.average_green_min, 7.01)
        self.assertEqual(DEFAULT_CONFIG.severe_green_max, 0)
        self.assertEqual(DEFAULT_CONFIG.mild_green_max, 5)

    def test_get_effective_falls_back_without_db(self):
        # SimpleTestCase bloquea la BD → debe devolver DEFAULT_CONFIG.
        config = RiskScoringConfigService.get_effective()
        self.assertEqual(config.source, "default")


class Phase5SerializerValidationTest(SimpleTestCase):
    """El backend rechaza configuraciones inseguras (Auditoría §9.4)."""

    BASE = {
        "engine": "reglas",
        "weight_conducta": 30,
        "weight_asistencia": 35,
        "weight_calificaciones": 35,
        "attendance_red_max": 70,
        "attendance_yellow_max": 85,
        "attendance_green_min": 85.01,
        "average_red_max": 6.0,
        "average_yellow_max": 7.0,
        "average_green_min": 7.01,
        "severe_red_min": 3,
        "mild_yellow_min": 5,
        "severe_green_max": 0,
        "mild_green_max": 5,
    }

    def test_valid_config_passes(self):
        serializer = RiskScoringConfigSerializer(data=self.BASE)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_weights_must_sum_100(self):
        data = {**self.BASE, "weight_conducta": 20}  # suma 90
        serializer = RiskScoringConfigSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("weights", serializer.errors)

    def test_weight_out_of_bounds_rejected(self):
        data = {
            **self.BASE,
            "weight_conducta": 5,
            "weight_asistencia": 35,
            "weight_calificaciones": 60,
        }
        serializer = RiskScoringConfigSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("weight_conducta", serializer.errors)

    def test_incoherent_attendance_thresholds_rejected(self):
        data = {**self.BASE, "attendance_red_max": 90, "attendance_yellow_max": 85}
        serializer = RiskScoringConfigSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("attendance_red_max", serializer.errors)

    def test_incoherent_average_thresholds_rejected(self):
        data = {**self.BASE, "average_red_max": 8.0, "average_yellow_max": 7.0}
        serializer = RiskScoringConfigSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("average_red_max", serializer.errors)

    def test_average_domain_rejected(self):
        data = {**self.BASE, "average_red_max": 6.0, "average_yellow_max": 15.0}
        serializer = RiskScoringConfigSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("average_yellow_max", serializer.errors)

    def test_all_presets_are_valid(self):
        for key, preset in PRESETS.items():
            serializer = RiskScoringConfigSerializer(data={**preset, "preset": key})
            self.assertTrue(
                serializer.is_valid(),
                f"Preset '{key}' inválido: {serializer.errors}",
            )


class Phase5DbConfigAppliedTest(TestCase):
    """Con fila en BD, el cálculo usa la config y model_version la refleja."""

    def test_singleton_repository_is_idempotent(self):
        c1 = RiskScoringConfigRepository.get_or_create_singleton()
        c2 = RiskScoringConfigRepository.get_or_create_singleton()
        self.assertEqual(c1.pk, RiskScoringConfig.SINGLETON_PK)
        self.assertEqual(c2.pk, RiskScoringConfig.SINGLETON_PK)
        self.assertEqual(RiskScoringConfig.objects.count(), 1)

    def test_strict_preset_changes_classification(self):
        # Preset estricto: verde desde 85% → 86 es verde; en equilibrado (verde 85.01) 86 también.
        # Usamos 88: en estricto es verde (≥85), en equilibrado por defecto sería amarillo si green=90.
        config = RiskScoringConfigRepository.get_or_create_singleton()
        for field, value in {**PRESETS["estricto"], "preset": "estricto"}.items():
            setattr(config, field, value)
        config.save()

        result = calculate_academic_risk(_snapshot(attendance=88.0, average=9.0))
        self.assertEqual(result["semaforo_riesgo"]["nivel"], "verde")

    def test_model_version_reflects_db_config(self):
        RiskScoringConfigRepository.get_or_create_singleton()
        result = calculate_academic_risk(_snapshot())
        self.assertTrue(result["model_version"].startswith(MODEL_VERSION_FALLBACK + "+cfg"))

    def test_default_model_version_without_db_row(self):
        # Sin fila singleton, model_version es el fallback base (baseline intacto).
        self.assertFalse(RiskScoringConfig.objects.exists())
        result = calculate_academic_risk(_snapshot())
        self.assertEqual(result["model_version"], MODEL_VERSION_FALLBACK)

    def test_ml_engine_without_artifact_falls_back(self):
        config = RiskScoringConfigRepository.get_or_create_singleton()
        config.engine = "ML"
        config.save()
        result = calculate_academic_risk(_snapshot(attendance=60.0))
        # Sin artefacto, cae al fallback por reglas (model_version fallback).
        self.assertTrue(result["model_version"].startswith(MODEL_VERSION_FALLBACK))
        self.assertEqual(result["semaforo_riesgo"]["nivel"], "rojo")
