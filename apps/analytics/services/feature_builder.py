"""
Construccion de snapshots de riesgo academico desde grading.
"""

from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from apps.academic.repositories.academic_repo import AcademicPeriodRepository
from apps.grading.repositories import (
    AttendanceRepository,
    ConductIncidentRepository,
    StudentNoteRepository,
)
from apps.students.repositories.students_repo import StudentRepository


PASSING_GRADE = Decimal("7.00")


def _decimal(value, default="0.00"):
    if value is None:
        value = default
    return Decimal(str(value))


def _round_decimal(value):
    return _decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


class AcademicRiskFeatureBuilder:
    """
    Construye el snapshot JSON de entrada para el modelo de riesgo academico.
    """

    def __init__(self, student_id, academic_period_id):
        self.student_id = student_id
        self.academic_period_id = academic_period_id

    def build(self):
        student = StudentRepository.get_by_id(self.student_id)
        if not student:
            raise ValueError(f"Estudiante {self.student_id} no encontrado")

        period = AcademicPeriodRepository.get_by_id(self.academic_period_id)
        if not period:
            raise ValueError(f"Periodo academico {self.academic_period_id} no encontrado")

        attendances = list(
            AttendanceRepository.list_for_risk_snapshot(
                self.student_id, self.academic_period_id
            )
        )
        incidents = list(
            ConductIncidentRepository.list_for_risk_snapshot(
                self.student_id, self.academic_period_id
            )
        )
        notes = list(
            StudentNoteRepository.list_for_risk_snapshot(
                self.student_id, self.academic_period_id
            )
        )

        conducta = self._build_conduct(incidents)
        asistencia = self._build_attendance(attendances)
        calificaciones = self._build_grades(notes)

        snapshot = {
            "estudiante_id": str(student.id),
            "periodo": str(period.id),
            "variables": {
                "conducta": conducta,
                "asistencia": asistencia,
                "calificaciones": calificaciones,
            },
        }
        self.validate_snapshot(snapshot)
        return snapshot

    def build_persistence_metrics(self, snapshot):
        variables = snapshot["variables"]
        conducta = variables["conducta"]
        asistencia = variables["asistencia"]
        calificaciones = variables["calificaciones"]

        conduct_score = self._calculate_conduct_score(
            conducta["faltas_leves"],
            conducta.get("faltas_moderadas", 0),
            conducta["faltas_graves"],
        )

        return {
            "attendance_rate": _round_decimal(asistencia["porcentaje_asistencia"]),
            "consecutive_absences_max": asistencia["max_faltas_consecutivas"],
            "tardiness_count": asistencia["tardanzas"],
            "avg_grade_normalized": _round_decimal(calificaciones["promedio_actual"]),
            "grade_trend_slope": _round_decimal(calificaciones["tendencia_notas"]),
            "failing_subjects_count": calificaciones["materias_reprobadas"],
            "conduct_score": _round_decimal(conduct_score),
            "family_notified_ratio": _round_decimal(conducta["ratio_notificacion_familiar"]),
            "prev_period_avg_grade": None,
            "age_grade_gap": 0,
        }

    def validate_snapshot(self, snapshot):
        variables = snapshot.get("variables", {})
        conducta = variables.get("conducta", {})
        asistencia = variables.get("asistencia", {})
        calificaciones = variables.get("calificaciones", {})

        self._validate_non_negative(conducta, "faltas_leves")
        self._validate_non_negative(conducta, "faltas_graves")
        self._validate_non_negative(asistencia, "total_faltas")
        self._validate_non_negative(asistencia, "faltas_justificadas")
        self._validate_non_negative(asistencia, "faltas_injustificadas")
        self._validate_range(
            asistencia.get("porcentaje_asistencia"), 0, 100, "porcentaje_asistencia"
        )
        self._validate_range(calificaciones.get("promedio_actual"), 0, 10, "promedio_actual")
        self._validate_range(calificaciones.get("ultimo_examen"), 0, 10, "ultimo_examen")
        self._validate_non_negative(calificaciones, "materias_reprobadas")
        self._validate_non_negative(calificaciones, "tareas_entregadas")
        self._validate_non_negative(calificaciones, "tareas_pendientes")

    def _build_conduct(self, incidents):
        leves = sum(1 for incident in incidents if incident.severity == 1)
        moderadas = sum(1 for incident in incidents if incident.severity == 2)
        graves = sum(1 for incident in incidents if incident.severity == 3)
        descriptions = [
            incident.description.strip()
            for incident in incidents[:3]
            if incident.description and incident.description.strip()
        ]
        latest = incidents[0].updated_at.date() if incidents else None
        notified = sum(1 for incident in incidents if incident.family_notified)
        notified_ratio = (notified / len(incidents)) if incidents else 0

        return {
            "faltas_leves": leves,
            "faltas_moderadas": moderadas,
            "faltas_graves": graves,
            "observaciones": " | ".join(descriptions),
            "ultima_actualizacion": latest.isoformat() if latest else None,
            "ratio_notificacion_familiar": round(notified_ratio, 2),
        }

    def _build_attendance(self, attendances):
        total = len(attendances)
        presentes = sum(1 for attendance in attendances if attendance.attendance_status and attendance.attendance_status.code == "P")
        justificadas = sum(1 for attendance in attendances if attendance.attendance_status and attendance.attendance_status.code == "J")
        injustificadas = sum(1 for attendance in attendances if attendance.attendance_status and attendance.attendance_status.code == "A")
        tardanzas = sum(1 for attendance in attendances if attendance.attendance_status and attendance.attendance_status.code == "T")
        porcentaje = (presentes / total * 100) if total else 0

        return {
            "porcentaje_asistencia": round(porcentaje, 2),
            "total_faltas": justificadas + injustificadas,
            "faltas_justificadas": justificadas,
            "faltas_injustificadas": injustificadas,
            "tardanzas": tardanzas,
            "total_registros": total,
            "max_faltas_consecutivas": self._max_consecutive_absences(attendances),
        }

    def _build_grades(self, notes):
        values = [_decimal(note.calculate_normalized_value()) for note in notes]
        average = sum(values, Decimal("0.00")) / len(values) if values else Decimal("0.00")
        last_exam = self._last_exam_grade(notes)

        return {
            "promedio_actual": float(_round_decimal(average)),
            "materias_reprobadas": self._count_failing_subjects(notes),
            "tareas_entregadas": 0,
            "tareas_pendientes": 0,
            "ultimo_examen": float(_round_decimal(last_exam)),
            "tendencia_notas": float(_round_decimal(self._grade_trend(values))),
            "total_calificaciones": len(notes),
        }

    def _count_failing_subjects(self, notes):
        subject_values = defaultdict(list)
        for note in notes:
            subject_id = note.class_assignment.teacher_subject_section.subject_offering.subject_academic_config.subject_id
            subject_values[subject_id].append(_decimal(note.calculate_normalized_value()))

        failing = 0
        for values in subject_values.values():
            average = sum(values, Decimal("0.00")) / len(values)
            if average < PASSING_GRADE:
                failing += 1
        return failing

    def _last_exam_grade(self, notes):
        exam_notes = [
            note
            for note in notes
            if note.class_assignment
            and "examen" in note.class_assignment.title.lower()
        ]
        source = exam_notes or notes
        if not source:
            return Decimal("0.00")
        return _decimal(source[-1].calculate_normalized_value())

    def _grade_trend(self, values):
        if len(values) < 2:
            return Decimal("0.00")
        return (values[-1] - values[0]) / Decimal(len(values) - 1)

    def _max_consecutive_absences(self, attendances):
        max_streak = 0
        current = 0
        for attendance in attendances:
            if attendance.attendance_status and attendance.attendance_status.code in ("A", "J"):
                current += 1
                max_streak = max(max_streak, current)
            else:
                current = 0
        return max_streak

    def _calculate_conduct_score(self, leves, moderadas, graves):
        penalty = Decimal(leves) * Decimal("0.50")
        penalty += Decimal(moderadas) * Decimal("1.00")
        penalty += Decimal(graves) * Decimal("2.00")
        return _clamp(Decimal("10.00") - penalty, Decimal("0.00"), Decimal("10.00"))

    def _validate_non_negative(self, data, key):
        value = data.get(key)
        if value is None or value < 0:
            raise ValueError(f"{key} debe ser un numero no negativo")

    def _validate_range(self, value, minimum, maximum, key):
        if value is None or value < minimum or value > maximum:
            raise ValueError(f"{key} debe estar entre {minimum} y {maximum}")
