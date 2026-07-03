from datetime import date, timedelta
from decimal import Decimal
from dataclasses import replace
from unittest.mock import patch

from django.test import TestCase

from apps.analytics.services.risk_scoring_config_service import DEFAULT_CONFIG
from apps.analytics.student_risk.domain.risk_engine import calculate_risk

from apps.institutions.models import Section
from apps.academic.period_type import PeriodType
from apps.academic.academic_period import AcademicPeriod
from apps.academic.subject import Subject
from apps.academic.subject_academic_config import SubjectAcademicConfig
from apps.academic.subject_offering import SubjectOffering
from apps.academic.teacher_subject_section import TeacherSubjectSection
from apps.iam.models import Role, User
from apps.core.tests.helpers import create_test_user, create_test_student
from apps.analytics.student_risk.infrastructure.models import StudentFeatureSnapshot, StudentRiskScore
from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder
from apps.analytics.tasks import (
    calculate_academic_risk,
    calculate_student_academic_risk_task,
)
from apps.grading.evaluation import (
    BlockComponent,
    EvaluationBlock,
    EvaluativeActivity,
)
from apps.grading.student_note import StudentNote
from apps.grading.activity_type import ActivityType
from apps.behavior.severity import Severity
from apps.attendance.attendance_core import Attendance
from apps.behavior.conduct_incident import ConductIncident
from apps.attendance.attendance_status import AttendanceStatus
from apps.behavior.incident_type import IncidentType
from apps.institutions.models import AcademicLevel, AcademicGrade, AcademicSublevel, SchoolYear
from apps.students.models import Enrollment, Student


class AcademicRiskModelTest(TestCase):
    def setUp(self):
        self.school_year = SchoolYear.objects.create(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )
        self.period = AcademicPeriod.objects.create(
            school_year=self.school_year,
            name="P1",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
        )
        self.academic_level = AcademicLevel.objects.create(name="Basica")
        self.academic_sublevel = AcademicSublevel.objects.create(
            academic_level=self.academic_level, name="Básica"
        )
        self.academic_grade = AcademicGrade.objects.create(
            academic_sublevel=self.academic_sublevel, name="8"
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            academic_grade=self.academic_grade,
            parallel="A",
            capacity=30,
        )
        self.subject = Subject.objects.create(
            name="Matematica",
            code="MAT-8A",
        )
        self.role = Role.objects.create(name="Docente")
        self.teacher = create_test_user(
            email="docente@example.com",
            dni="0102030405",
            names="Ana",
            last_names="Perez",
        )
        subj_config = SubjectAcademicConfig.objects.create(
            subject=self.subject,
            academic_grade=self.academic_grade,
            weekly_hours=5        )
        offering = SubjectOffering.objects.create(
            section=self.section,
            subject_academic_config=subj_config,
        )
        self.teacher_subject_section = TeacherSubjectSection.objects.create(
            user=self.teacher,
            subject_offering=offering,
        )
        self.offering = offering
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
        self.attendance_statuses = {}
        for code, name in [
            ("P", "Presente"),
            ("A", "Ausente"),
            ("T", "Tardanza"),
            ("J", "Justificado"),
        ]:
            s, _ = AttendanceStatus.objects.get_or_create(
                code=code, defaults={"name": name}
            )
            self.attendance_statuses[code] = s

        self.activity_type_exam = ActivityType.objects.create(code="EXAMEN", name="Examen")
        self.severity_leve = Severity.objects.create(
            code="LEVE", name="Falta leve",
        )
        self.exam = self._create_evaluative_activity("Examen parcial", 10)
        self.homework = self._create_evaluative_activity("Tarea 1", 10)

    def _create_evaluative_activity(self, title, max_score=10):
        block = EvaluationBlock.objects.create(
            academic_period=self.period,
            subject_offering=self.offering,
            name=f"Bloque-{title}",
            block_type="FORMATIVA",
            weight_percentage=Decimal("100.00"),
        )
        component = BlockComponent.objects.create(
            evaluation_block=block,
            name=f"Componente-{title}",
            internal_weight=Decimal("100.00"),
        )
        return EvaluativeActivity.objects.create(
            block_component=component,
            teacher_subject_section=self.teacher_subject_section,
            title=title,
            activity_type=self.activity_type_exam,
            max_score=Decimal(str(max_score)),
            internal_weight=Decimal("100.00"),
            due_date=date(2026, 2, 1),
        )

    def _create_attendance_sequence(self, statuses):
        start = date(2026, 1, 10)
        for index, status in enumerate(statuses):
            Attendance.objects.create(
                enrollment=self.enrollment,
                teacher_subject_section=self.teacher_subject_section,
                academic_period=self.period,
                attendance_date=start + timedelta(days=index),
                attendance_status=self.attendance_statuses.get(status),
            )

    def _create_note(self, evaluative_activity, value):
        StudentNote.objects.create(
            enrollment=self.enrollment,
            evaluative_activity=evaluative_activity,
            numeric_score=Decimal(str(value)),
        )

    def _base_snapshot(self):
        return {
            "estudiante_id": str(self.student.id),
            "periodo": str(self.period.id),
            "variables": {
                "conducta": {
                    "faltas_leves": 0,
                    "faltas_moderadas": 0,
                    "faltas_graves": 0,
                    "observaciones": "",
                    "ultima_actualizacion": None,
                    "ratio_notificacion_familiar": 0,
                },
                "asistencia": {
                    "porcentaje_asistencia": 90.0,
                    "total_faltas": 1,
                    "faltas_justificadas": 0,
                    "faltas_injustificadas": 1,
                    "tardanzas": 0,
                    "total_registros": 10,
                    "max_faltas_consecutivas": 1,
                },
                "calificaciones": {
                    "promedio_actual": 8.0,
                    "materias_reprobadas": 0,
                    "ultimo_examen": 8.0,
                    "tendencia_notas": 0.0,
                    "total_calificaciones": 1,
                },
            },
        }

    def test_feature_builder_creates_complete_snapshot(self):
        inc_type = IncidentType.objects.create(code="disciplina", name="Disciplina")
        self._create_attendance_sequence(["P", "P", "A", "J", "T"])
        self._create_note(self.exam, 8)
        ConductIncident.objects.create(
            enrollment=self.enrollment,
            academic_period=self.period,
            incident_type=inc_type,
            incident_date=date(2026, 1, 20),
            severity=self.severity_leve,
            description="Llega sin materiales",
            family_notified=True,
        )

        snapshot = AcademicRiskFeatureBuilder(self.student.id, self.period.id).build()

        self.assertEqual(snapshot["estudiante_id"], str(self.student.id))
        self.assertEqual(snapshot["variables"]["conducta"]["faltas_leves"], 1)
        self.assertEqual(snapshot["variables"]["asistencia"]["total_faltas"], 2)
        self.assertEqual(
            snapshot["variables"]["asistencia"]["porcentaje_asistencia"], 40.0
        )
        self.assertEqual(
            snapshot["variables"]["calificaciones"]["promedio_actual"], 8.0
        )
        self.assertEqual(snapshot["variables"]["calificaciones"]["ultimo_examen"], 8.0)

    def test_feature_builder_imputes_missing_data(self):
        snapshot = AcademicRiskFeatureBuilder(self.student.id, self.period.id).build()

        self.assertEqual(snapshot["variables"]["conducta"]["faltas_graves"], 0)
        self.assertEqual(
            snapshot["variables"]["asistencia"]["porcentaje_asistencia"], 0
        )
        self.assertEqual(
            snapshot["variables"]["calificaciones"]["promedio_actual"], 0.0
        )
        self.assertEqual(
            snapshot["variables"]["calificaciones"]["materias_reprobadas"], 0
        )
        # §6.2: las features muertas tareas_entregadas/pendientes ya no existen.
        self.assertNotIn(
            "tareas_pendientes", snapshot["variables"]["calificaciones"]
        )

    def test_risk_rules_red_by_low_attendance(self):
        snapshot = self._base_snapshot()
        snapshot["variables"]["asistencia"]["porcentaje_asistencia"] = 60.0

        result = calculate_academic_risk(snapshot)

        self.assertEqual(result["semaforo_riesgo"]["nivel"], "rojo")

    def test_risk_rules_red_by_low_average(self):
        snapshot = self._base_snapshot()
        snapshot["variables"]["calificaciones"]["promedio_actual"] = 5.5

        result = calculate_academic_risk(snapshot)

        self.assertEqual(result["semaforo_riesgo"]["nivel"], "rojo")

    def test_risk_rules_red_by_severe_incidents(self):
        snapshot = self._base_snapshot()
        snapshot["variables"]["conducta"]["faltas_graves"] = 4

        result = calculate_academic_risk(snapshot)

        self.assertEqual(result["semaforo_riesgo"]["nivel"], "rojo")

    def test_risk_rules_yellow(self):
        snapshot = self._base_snapshot()
        snapshot["variables"]["asistencia"]["porcentaje_asistencia"] = 80.0

        result = calculate_academic_risk(snapshot)

        self.assertEqual(result["semaforo_riesgo"]["nivel"], "amarillo")

    def test_risk_rules_green(self):
        result = calculate_academic_risk(self._base_snapshot())

        self.assertEqual(result["semaforo_riesgo"]["nivel"], "verde")

    @patch("apps.analytics.student_risk.domain.risk_engine._predict_ml_score", return_value=98.0)
    def test_semaphore_level_follows_ml_score_not_rule_band(self, _mocked_ml):
        """Puntaje ML alto debe clasificar en rojo aunque las reglas digan amarillo."""
        config = replace(DEFAULT_CONFIG, engine="ML")
        snapshot = self._base_snapshot()
        snapshot["variables"]["asistencia"]["porcentaje_asistencia"] = 80.0

        result = calculate_risk(snapshot, config=config)

        self.assertEqual(result["semaforo_riesgo"]["puntaje_riesgo"], 98.0)
        self.assertEqual(result["semaforo_riesgo"]["nivel"], "rojo")

    @patch("apps.analytics.tasks._predict_ml_score", return_value=None)
    def test_task_returns_json_and_persists_fallback_result(self, mocked_predict):
        self._create_attendance_sequence(["P"] * 9 + ["A"])
        self._create_note(self.exam, 8)

        result = calculate_student_academic_risk_task(self.student.id, self.period.id)

        self.assertEqual(result["semaforo_riesgo"]["nivel"], "verde")
        self.assertTrue(
            StudentFeatureSnapshot.objects.filter(enrollment__student=self.student).exists()
        )
        self.assertTrue(StudentRiskScore.objects.filter(enrollment__student=self.student).exists())
        self.assertNotIn("model_version", result)
        # Fase 5: con el motor por defecto ("reglas") NO se invoca el ML; el
        # cálculo usa directamente el fallback por reglas (ML sólo con engine=ML).
        mocked_predict.assert_not_called()


class SimulateRiskEnginesTest(TestCase):
    """El simulador debe evaluar reglas y ML por separado."""

    BASE_PARAMS = {
        "attendance_rate": 85.0,
        "average_grade": 7.0,
        "failing_subjects_count": 0,
        "severe_incidents_count": 0,
        "mild_incidents_count": 1,
    }

    @patch(
        "apps.analytics.student_risk.domain.risk_engine._predict_ml_score",
        return_value=92.0,
    )
    def test_simulate_rules_ignore_ml_even_when_production_uses_ml(self, _mock_ml):
        from apps.analytics.student_risk.domain.services import StudentRiskCalculationService

        result = StudentRiskCalculationService.simulate(
            {
                **self.BASE_PARAMS,
                "config_overrides": {"engine": "ML"},
            }
        )

        self.assertIn("rules-fallback", result["reglas"]["model_version"])
        self.assertEqual(result["reglas"]["motor"], "reglas")
        self.assertLess(result["reglas"]["semaforo_riesgo"]["puntaje_riesgo"], 90)
        self.assertEqual(result["ml"]["puntaje_riesgo"], 92.0)
        self.assertEqual(result["produccion"]["semaforo_riesgo"]["puntaje_riesgo"], 92.0)
        self.assertEqual(result["produccion"]["motor"], "ML")


class SimulateRiskEnginesTest(TestCase):
  """El simulador debe evaluar reglas y ML por separado."""

  BASE_PARAMS = {
      "attendance_rate": 85.0,
      "average_grade": 7.0,
      "failing_subjects_count": 0,
      "severe_incidents_count": 0,
      "mild_incidents_count": 1,
  }

  @patch(
      "apps.analytics.student_risk.domain.risk_engine._predict_ml_score",
      return_value=92.0,
  )
  def test_simulate_rules_ignore_ml_even_when_production_uses_ml(self, _mock_ml):
      from apps.analytics.student_risk.domain.services import StudentRiskCalculationService

      result = StudentRiskCalculationService.simulate(
          {
              **self.BASE_PARAMS,
              "config_overrides": {"engine": "ML"},
          }
      )

      self.assertIn("rules-fallback", result["reglas"]["model_version"])
      self.assertLess(result["reglas"]["semaforo_riesgo"]["puntaje_riesgo"], 90)
      self.assertEqual(result["ml"]["puntaje_riesgo"], 92.0)
      self.assertEqual(result["produccion"]["semaforo_riesgo"]["puntaje_riesgo"], 92.0)
      self.assertEqual(result["produccion"]["motor"], "ML")
