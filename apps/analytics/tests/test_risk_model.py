from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from apps.academic.models import (
    Academic_Activity,
    Academic_Period,
    Config_Academic,
    Section,
    Subject,
    Teacher_Subject_Section,
)
from apps.accounts.models import Role, User
from apps.analytics.models import StudentFeatureSnapshot, StudentRiskScore
from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder
from apps.analytics.tasks import calculate_academic_risk, calculate_student_academic_risk_task
from apps.grading.models import Attendance, ConductIncident, StudentNote
from apps.institutions.models import Institution, School_Year
from apps.students.models import Student


class AcademicRiskModelTest(TestCase):
    def setUp(self):
        self.institution = Institution.objects.create(
            name="Colegio Test",
            code="COL-001",
            address="Calle 1",
            city="Quito",
        )
        self.school_year = School_Year.objects.create(
            institution=self.institution,
            name="2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )
        self.config = Config_Academic.objects.create(
            school_year=self.school_year,
            institution=self.institution,
            name="Config 2026",
            academic_period_type="trimestre",
            number_of_periods=3,
        )
        self.period = Academic_Period.objects.create(
            config_academic=self.config,
            name="P1",
            number=1,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
        )
        self.section = Section.objects.create(
            school_year=self.school_year,
            timing_regime=None,
            level="Basica",
            grade="8",
            parallel="A",
            capacity=30,
        )
        self.subject = Subject.objects.create(
            school_year=self.school_year,
            section=self.section,
            name="Matematica",
            code="MAT-8A",
            weekly_hours=5,
            approve_percentage=70,
        )
        self.role = Role.objects.create(name="Docente")
        self.teacher = User.objects.create_user(
            email="docente@example.com",
            dni="0102030405",
            names="Ana",
            last_names="Perez",
            password="secret",
            role=self.role,
            institution=self.institution,
        )
        self.teacher_subject_section = Teacher_Subject_Section.objects.create(
            user=self.teacher,
            subject=self.subject,
            section=self.section,
            school_year=self.school_year,
        )
        self.exam = Academic_Activity.objects.create(
            config_academic=self.config,
            subject=self.subject,
            name="Examen parcial",
            value_max=10,
            weight=1,
            applies_to="all",
            order=1,
        )
        self.homework = Academic_Activity.objects.create(
            config_academic=self.config,
            subject=self.subject,
            name="Tarea 1",
            value_max=10,
            weight=1,
            applies_to="all",
            order=2,
        )
        self.student = Student.objects.create(
            dni="0912345678",
            names="Juan",
            last_names="Lopez",
            birth_date=date(2012, 1, 1),
            section=self.section,
        )

    def _create_attendance_sequence(self, statuses):
        start = date(2026, 1, 10)
        for index, status in enumerate(statuses):
            Attendance.objects.create(
                student=self.student,
                teacher_subject_section=self.teacher_subject_section,
                academic_period=self.period,
                date=start + timedelta(days=index),
                status=status,
            )

    def _create_note(self, activity, value):
        StudentNote.objects.create(
            student=self.student,
            academic_activity=activity,
            academic_period=self.period,
            teacher_subject_section=self.teacher_subject_section,
            note_value=Decimal(str(value)),
            normalized_value=Decimal(str(value)),
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
                    "tareas_entregadas": 0,
                    "tareas_pendientes": 0,
                    "ultimo_examen": 8.0,
                    "tendencia_notas": 0.0,
                    "total_calificaciones": 1,
                },
            },
        }

    def test_feature_builder_creates_complete_snapshot(self):
        self._create_attendance_sequence(["P", "P", "A", "J", "T"])
        self._create_note(self.exam, 8)
        ConductIncident.objects.create(
            student=self.student,
            reported_by=self.teacher,
            academic_period=self.period,
            incident_date=date(2026, 1, 20),
            category="disciplina",
            severity=1,
            description="Llega sin materiales",
            family_notified=True,
        )

        snapshot = AcademicRiskFeatureBuilder(self.student.id, self.period.id).build()

        self.assertEqual(snapshot["estudiante_id"], str(self.student.id))
        self.assertEqual(snapshot["variables"]["conducta"]["faltas_leves"], 1)
        self.assertEqual(snapshot["variables"]["asistencia"]["total_faltas"], 2)
        self.assertEqual(snapshot["variables"]["asistencia"]["porcentaje_asistencia"], 40.0)
        self.assertEqual(snapshot["variables"]["calificaciones"]["promedio_actual"], 8.0)
        self.assertEqual(snapshot["variables"]["calificaciones"]["ultimo_examen"], 8.0)

    def test_feature_builder_imputes_missing_data(self):
        snapshot = AcademicRiskFeatureBuilder(self.student.id, self.period.id).build()

        self.assertEqual(snapshot["variables"]["conducta"]["faltas_graves"], 0)
        self.assertEqual(snapshot["variables"]["asistencia"]["porcentaje_asistencia"], 0)
        self.assertEqual(snapshot["variables"]["calificaciones"]["promedio_actual"], 0.0)
        self.assertEqual(snapshot["variables"]["calificaciones"]["tareas_pendientes"], 0)

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

    @patch("apps.analytics.tasks._predict_ml_score", return_value=None)
    def test_task_returns_json_and_persists_fallback_result(self, mocked_predict):
        self._create_attendance_sequence(["P"] * 9 + ["A"])
        self._create_note(self.exam, 8)

        result = calculate_student_academic_risk_task(self.student.id, self.period.id)

        self.assertEqual(result["semaforo_riesgo"]["nivel"], "verde")
        self.assertTrue(StudentFeatureSnapshot.objects.filter(student=self.student).exists())
        self.assertTrue(StudentRiskScore.objects.filter(student=self.student).exists())
        self.assertNotIn("model_version", result)
        mocked_predict.assert_called_once()
