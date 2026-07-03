"""
Fase 0 — Baseline y red de seguridad (PLAN_IMPLEMENTACION.md).

Estos tests CONGELAN el comportamiento vigente del cálculo de riesgo académico
para poder detectar regresiones cuando se ejecuten las fases siguientes
(que modifican el score productivo).

Cubren:
- Confirmación de que NO existe `risk_model.joblib` (todo corre por fallback).
- `_risk_level` (umbrales del semáforo).
- `_fallback_risk_score` (puntaje por reglas + pisos/topes por nivel).
- `calculate_academic_risk` extremo a extremo contra el snapshot dorado
  (`baseline_scores.json`).
- `EarlyAlertService.evaluate_student` (reglas de alertas tempranas).
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase

from apps.analytics.tasks import (
    MODEL_PATH,
    MODEL_VERSION_FALLBACK,
    WEIGHTS,
    _fallback_risk_score,
    _risk_level,
    _score_to_level,
    calculate_academic_risk,
)

BASELINE_FILE = Path(__file__).resolve().parent / "baseline_scores.json"


def _load_baseline():
    with open(BASELINE_FILE, encoding="utf-8") as fh:
        return json.load(fh)


def _full_snapshot(variables, estudiante_id="1", periodo="1"):
    """Completa el snapshot con las claves que consume calculate_academic_risk."""
    conducta = {
        "faltas_leves": 0,
        "faltas_moderadas": 0,
        "faltas_graves": 0,
        **variables.get("conducta", {}),
    }
    asistencia = {
        "porcentaje_asistencia": 0.0,
        "total_registros": 0,
        "total_faltas": 0,
        "faltas_injustificadas": 0,
        **variables.get("asistencia", {}),
    }
    calificaciones = {
        "promedio_actual": 0.0,
        "materias_reprobadas": 0,
        "total_calificaciones": 0,
        "ultimo_examen": 0.0,
        **variables.get("calificaciones", {}),
    }
    return {
        "estudiante_id": estudiante_id,
        "periodo": periodo,
        "variables": {
            "conducta": conducta,
            "asistencia": asistencia,
            "calificaciones": calificaciones,
        },
    }


class Phase0ModelAbsenceTest(SimpleTestCase):
    """El baseline asume que el sistema corre 100% por fallback de reglas."""

    def test_ml_model_artifact_is_absent(self):
        self.assertFalse(
            MODEL_PATH.exists(),
            "El baseline de Fase 0 asume que NO existe risk_model.joblib. "
            "Si ya se entrenó un modelo, este baseline debe regenerarse.",
        )

    def test_weights_are_frozen(self):
        self.assertEqual(
            WEIGHTS,
            {"conducta": 0.30, "asistencia": 0.35, "calificaciones": 0.35},
        )


class Phase0RiskLevelBoundaryTest(SimpleTestCase):
    """Congela los umbrales exactos de _risk_level."""

    def _vars(self, attendance=95.0, average=9.0, severe=0, mild=0):
        return {
            "conducta": {"faltas_leves": mild, "faltas_moderadas": 0, "faltas_graves": severe},
            "asistencia": {"porcentaje_asistencia": attendance},
            "calificaciones": {"promedio_actual": average},
        }

    def test_red_when_attendance_below_70(self):
        self.assertEqual(_risk_level(self._vars(attendance=69.99)), "rojo")

    def test_red_when_average_below_6(self):
        self.assertEqual(_risk_level(self._vars(average=5.99)), "rojo")

    def test_red_when_severe_incidents_above_3(self):
        self.assertEqual(_risk_level(self._vars(severe=4)), "rojo")

    def test_yellow_at_attendance_70(self):
        self.assertEqual(_risk_level(self._vars(attendance=70.0)), "amarillo")

    def test_yellow_at_attendance_85(self):
        self.assertEqual(_risk_level(self._vars(attendance=85.0)), "amarillo")

    def test_yellow_at_average_6(self):
        self.assertEqual(_risk_level(self._vars(average=6.0)), "amarillo")

    def test_yellow_at_average_7(self):
        self.assertEqual(_risk_level(self._vars(average=7.0)), "amarillo")

    def test_yellow_when_mild_above_5(self):
        self.assertEqual(_risk_level(self._vars(mild=6)), "amarillo")

    def test_green_when_all_healthy(self):
        self.assertEqual(_risk_level(self._vars(attendance=86.0, average=7.01)), "verde")


class Phase0ScoreToLevelTest(SimpleTestCase):
    """El semáforo publicado debe derivarse del puntaje final."""

    def test_thresholds(self):
        self.assertEqual(_score_to_level(0), "verde")
        self.assertEqual(_score_to_level(39.99), "verde")
        self.assertEqual(_score_to_level(40), "amarillo")
        self.assertEqual(_score_to_level(69.99), "amarillo")
        self.assertEqual(_score_to_level(70), "rojo")
        self.assertEqual(_score_to_level(98), "rojo")


class Phase0FallbackScoreTest(SimpleTestCase):
    """Congela la fórmula y los pisos/topes por nivel de _fallback_risk_score."""

    def test_green_profile_uses_weighted_formula(self):
        variables = {
            "conducta": {"faltas_leves": 0, "faltas_moderadas": 0, "faltas_graves": 0},
            "asistencia": {"porcentaje_asistencia": 95.0},
            "calificaciones": {"promedio_actual": 9.0, "materias_reprobadas": 0},
        }
        # 0*0.30 + (100-95)*0.35 + ((10-9)/10*100)*0.35 = 1.75 + 3.5 = 5.25
        self.assertAlmostEqual(_fallback_risk_score(variables, "verde"), 5.25, places=2)

    def test_yellow_level_applies_floor_of_40(self):
        variables = {
            "conducta": {"faltas_leves": 0, "faltas_moderadas": 0, "faltas_graves": 0},
            "asistencia": {"porcentaje_asistencia": 80.0},
            "calificaciones": {"promedio_actual": 7.0, "materias_reprobadas": 0},
        }
        self.assertAlmostEqual(_fallback_risk_score(variables, "amarillo"), 40.0, places=2)

    def test_red_level_applies_floor_of_70(self):
        variables = {
            "conducta": {"faltas_leves": 0, "faltas_moderadas": 0, "faltas_graves": 0},
            "asistencia": {"porcentaje_asistencia": 69.0},
            "calificaciones": {"promedio_actual": 9.0, "materias_reprobadas": 0},
        }
        self.assertAlmostEqual(_fallback_risk_score(variables, "rojo"), 70.0, places=2)

    def test_green_level_caps_at_3999(self):
        # Puntaje crudo alto (70) pero nivel forzado a verde -> el tope de 39.99 domina.
        variables = {
            "conducta": {"faltas_leves": 0, "faltas_moderadas": 0, "faltas_graves": 0},
            "asistencia": {"porcentaje_asistencia": 0.0},
            "calificaciones": {"promedio_actual": 0.0, "materias_reprobadas": 0},
        }
        self.assertAlmostEqual(_fallback_risk_score(variables, "verde"), 39.99, places=2)

    def test_score_is_bounded_0_100(self):
        variables = {
            "conducta": {"faltas_leves": 10, "faltas_moderadas": 10, "faltas_graves": 10},
            "asistencia": {"porcentaje_asistencia": 0.0},
            "calificaciones": {"promedio_actual": 0.0, "materias_reprobadas": 10},
        }
        score = _fallback_risk_score(variables, "rojo")
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)


class Phase0GoldenSnapshotTest(SimpleTestCase):
    """
    Compara calculate_academic_risk() contra el conjunto de referencia dorado
    (baseline_scores.json). Es la red de seguridad principal de la Fase 0.
    """

    def test_golden_profiles_match_reference(self):
        baseline = _load_baseline()
        self.assertEqual(WEIGHTS, baseline["weights"])

        failures = []
        for profile in baseline["profiles"]:
            snapshot = _full_snapshot(profile["variables"])
            result = calculate_academic_risk(snapshot)
            level = result["semaforo_riesgo"]["nivel"]
            score = result["semaforo_riesgo"]["puntaje_riesgo"]

            if level != _score_to_level(score):
                failures.append(
                    f"{profile['name']}: nivel {level} no coincide con puntaje {score}"
                )

            if level != profile["expected_level"]:
                failures.append(
                    f"{profile['name']}: nivel {level} != esperado {profile['expected_level']}"
                )
            if abs(score - profile["expected_score"]) > 0.01:
                failures.append(
                    f"{profile['name']}: score {score} != esperado {profile['expected_score']}"
                )
            self.assertEqual(result["model_version"], baseline["model_version_expected"])
            self.assertEqual(result["model_version"], MODEL_VERSION_FALLBACK)

        self.assertEqual(failures, [], "Regresión vs baseline dorado:\n" + "\n".join(failures))


class Phase0EarlyAlertServiceTest(TestCase):
    """
    Congela las reglas de EarlyAlertService.evaluate_student usando mocks de los
    repositorios, para fijar el comportamiento sin depender del esquema de datos.
    """

    def setUp(self):
        self.enrollment = MagicMock(id=1)
        self.period = MagicMock(id=10)

    def _run(self, attendance_summary, failing_count, severe_count):
        from apps.analytics.early_alert.domain.services import EarlyAlertService

        severe_qs = MagicMock()
        severe_qs.count.return_value = severe_count

        with patch(
            "apps.attendance.attendance_core.infrastructure.repositories.AttendanceRepository.get_absences_summary",
            return_value=attendance_summary,
        ), patch(
            "apps.grading.student_note.infrastructure.repositories.PeriodGradeSummaryRepository.count_failing",
            return_value=failing_count,
        ), patch(
            "apps.behavior.conduct_incident.infrastructure.repositories.ConductIncidentRepository.get_severe_by_enrollment",
            return_value=severe_qs,
        ), patch(
            "apps.analytics.early_alert.infrastructure.repositories.EarlyAlertRepository.create",
            side_effect=lambda **kwargs: kwargs,
        ):
            return EarlyAlertService.evaluate_student(self.enrollment, self.period)

    def test_no_alerts_when_all_healthy(self):
        alerts = self._run(
            attendance_summary={"total": 20, "unjustified": 1, "late": 0},
            failing_count=0,
            severe_count=0,
        )
        self.assertEqual(alerts, [])

    def test_low_attendance_medium_urgency(self):
        # rate = 1 - (7/20) = 0.65  -> < 0.7 y >= 0.5 -> MEDIUM
        alerts = self._run(
            attendance_summary={"total": 20, "unjustified": 7, "late": 0},
            failing_count=0,
            severe_count=0,
        )
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["alert_type"], "low_attendance")
        self.assertEqual(alerts[0]["urgency_level"], "medium")

    def test_low_attendance_high_urgency(self):
        # rate = 1 - (12/20) = 0.40 -> < 0.5 -> HIGH
        alerts = self._run(
            attendance_summary={"total": 20, "unjustified": 12, "late": 0},
            failing_count=0,
            severe_count=0,
        )
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["urgency_level"], "high")

    def test_failing_grades_requires_at_least_two(self):
        alerts = self._run(
            attendance_summary={"total": 20, "unjustified": 0, "late": 0},
            failing_count=1,
            severe_count=0,
        )
        self.assertEqual(alerts, [])

    def test_failing_grades_medium_then_high(self):
        medium = self._run(
            attendance_summary={"total": 20, "unjustified": 0, "late": 0},
            failing_count=2,
            severe_count=0,
        )
        self.assertEqual(len(medium), 1)
        self.assertEqual(medium[0]["alert_type"], "failing_grades")
        self.assertEqual(medium[0]["urgency_level"], "medium")

        high = self._run(
            attendance_summary={"total": 20, "unjustified": 0, "late": 0},
            failing_count=4,
            severe_count=0,
        )
        self.assertEqual(high[0]["urgency_level"], "high")

    def test_severe_incidents_trigger_critical(self):
        alerts = self._run(
            attendance_summary={"total": 20, "unjustified": 0, "late": 0},
            failing_count=0,
            severe_count=2,
        )
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["alert_type"], "behavioral")
        self.assertEqual(alerts[0]["urgency_level"], "critical")

    def test_all_rules_fire_together(self):
        alerts = self._run(
            attendance_summary={"total": 20, "unjustified": 12, "late": 0},
            failing_count=4,
            severe_count=3,
        )
        self.assertEqual(len(alerts), 3)
        types = {a["alert_type"] for a in alerts}
        self.assertEqual(types, {"low_attendance", "failing_grades", "behavioral"})
