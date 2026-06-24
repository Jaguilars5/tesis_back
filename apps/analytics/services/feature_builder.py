"""
Construccion de snapshots de riesgo academico desde grading.
"""

from decimal import Decimal, ROUND_HALF_UP

from apps.academic.repositories.academic_repo import AcademicPeriodRepository
from apps.attendance.repositories import AttendanceRepository
from apps.behavior.repositories import ConductIncidentRepository
from apps.grading.repositories import StudentNoteRepository
from apps.students.repositories.students_repo import StudentRepository


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
        # Fuente única de "materia reprobada": PeriodGradeSummary.is_failing (§6.4).
        # Misma definición que consume early_alert_service, garantizada por el
        # signal de grading que mantiene sincronizado el resumen.
        calificaciones["materias_reprobadas"] = self._count_failing_subjects(student)

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

        metrics = {
            "attendance_rate": _round_decimal(asistencia["porcentaje_asistencia"]),
            "consecutive_absences_max": asistencia["max_faltas_consecutivas"],
            "tardiness_count": asistencia["tardanzas"],
            "justified_absences": asistencia.get("faltas_justificadas", 0),
            "unjustified_absences": asistencia.get("faltas_injustificadas", 0),
            "avg_grade_normalized": _round_decimal(calificaciones["promedio_actual"]),
            "grade_trend_slope": _round_decimal(calificaciones["tendencia_notas"]),
            "failing_subjects_count": calificaciones["materias_reprobadas"],
            "conduct_score": _round_decimal(conduct_score),
            "severe_incidents_count": conducta.get("faltas_graves", 0),
            "family_notified_ratio": _round_decimal(conducta["ratio_notificacion_familiar"]),
        }

        student = StudentRepository.get_by_id(self.student_id)
        enrollment = self._get_active_enrollment(student)
        period = AcademicPeriodRepository.get_by_id(self.academic_period_id)

        metrics["prev_period_avg_grade"] = self._get_previous_period_avg(student, period)
        metrics["age_grade_gap"] = self._calculate_age_grade_gap(student, period)
        metrics["is_repeat"] = enrollment.is_repeat if enrollment else False
        metrics["has_special_needs"] = getattr(student, "has_special_needs", False)

        # Dimensiones analíticas / de segmentación (Fase 4 §5 F): ciudad de origen,
        # tipo de NEE y motivo de retiro. No alimentan el modelo numérico; sirven
        # para segmentar riesgo y deserción en dashboards/reportes.
        metrics["city_id"] = self._get_city_id(student)
        metrics["special_needs_type_id"] = getattr(student, "special_needs_type_id", None)
        metrics["withdrawal_reason_id"] = (
            enrollment.withdrawal_reason_id if enrollment else None
        )

        return metrics

    def _get_city_id(self, student):
        person = getattr(getattr(student, "user", None), "person", None)
        return getattr(person, "city_id", None) if person else None

    def _get_active_enrollment(self, student):
        if not student:
            return None
        from apps.students.repositories.enrollment_repo import EnrollmentRepository
        return EnrollmentRepository.get_active_by_student(student)

    def _get_previous_period_avg(self, student, current_period):
        if not current_period:
            return None
        prev_period_qs = type(current_period).objects.filter(
            school_year=current_period.school_year,
            start_date__lt=current_period.start_date,
        ).order_by("-start_date")
        prev_period = prev_period_qs.first()
        if not prev_period:
            return None
        enrollment = self._get_active_enrollment(student)
        if not enrollment:
            return None
        from apps.grading.student_note import PeriodGradeSummary
        summary = PeriodGradeSummary.objects.filter(
            enrollment=enrollment,
            academic_period=prev_period,
        ).first()
        return _round_decimal(summary.final_avg_truncated) if summary else None

    def _calculate_age_grade_gap(self, student, period):
        if not student or not period:
            return 0
        person = getattr(student, "person", None)
        if not person or not person.birth_date:
            return 0
        actual_age = (period.start_date - person.birth_date).days // 365
        expected_age = 5 + (getattr(period.school_year, "grade_level", 0) or 0)
        return max(0, actual_age - expected_age)

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

    def _build_conduct(self, incidents):
        leves_codes = {"LEVE"}
        moderadas_codes = {"MODERADA"}
        graves_codes = {"GRAVE", "MUY_GRAVE"}
        leves = sum(1 for incident in incidents if incident.severity.code in leves_codes)
        moderadas = sum(1 for incident in incidents if incident.severity.code in moderadas_codes)
        graves = sum(1 for incident in incidents if incident.severity.code in graves_codes)
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
            # Se sobreescribe en build() desde PeriodGradeSummary (fuente única, §6.4).
            "materias_reprobadas": 0,
            "ultimo_examen": float(_round_decimal(last_exam)),
            "tendencia_notas": float(_round_decimal(self._grade_trend(values))),
            "total_calificaciones": len(notes),
        }

    def _count_failing_subjects(self, student):
        """
        Cuenta materias reprobadas desde PeriodGradeSummary.is_failing (fuente única,
        §6.4) para la matrícula activa del estudiante en el periodo del snapshot.
        """
        enrollment = self._get_active_enrollment(student)
        if not enrollment:
            return 0
        from apps.grading.repositories.period_grade_summary_repository import (
            PeriodGradeSummaryRepository,
        )
        return PeriodGradeSummaryRepository.count_failing(
            enrollment.id, self.academic_period_id
        )

    def _last_exam_grade(self, notes):
        exam_notes = [
            note
            for note in notes
            if note.evaluative_activity
            and note.evaluative_activity.activity_type_id
            and note.evaluative_activity.activity_type.code == "EXAMEN"
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
