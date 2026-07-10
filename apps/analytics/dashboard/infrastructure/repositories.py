"""
Repositorio del dashboard analítico.

Centraliza TODA la consulta ORM de las métricas/reportes del dashboard
(checklist §4: "Toda consulta ORM debe vivir aquí"). Importa modelos de otras
apps únicamente en esta capa de infraestructura.
"""

from typing import Optional

from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncMonth

from apps.academic.academic_period.infrastructure.models import AcademicPeriod
from apps.academic.teacher_subject_section.infrastructure.models import (
    TeacherSubjectSection,
)
from apps.analytics.early_alert.infrastructure.models import EarlyAlert
from apps.analytics.student_risk.infrastructure.models import (
    StudentFeatureSnapshot,
    StudentRiskFactor,
    StudentRiskScore,
)
from apps.behavior.conduct_incident.infrastructure.models import ConductIncident
from apps.grading.evaluation.infrastructure.models import EvaluativeActivity
from apps.grading.student_note.infrastructure.models import (
    PeriodGradeSummary,
    StudentNote,
)
from apps.students.models import Enrollment


class DashboardRepository:
    """Acceso a datos para KPIs, distribuciones y reportes del dashboard."""

    # ── Helpers ──────────────────────────────────────────────────────────────
    @staticmethod
    def _label_counts(scores_qs) -> dict:
        """Cuenta puntajes por etiqueta de riesgo (rojo/amarillo/verde)."""
        counts = {"rojo": 0, "amarillo": 0, "verde": 0}
        for row in scores_qs.values("risk_label").annotate(n=Count("id")):
            if row["risk_label"] in counts:
                counts[row["risk_label"]] = row["n"]
        return counts

    # ── Período: snapshots y scores ──────────────────────────────────────────
    @classmethod
    def get_snapshot_aggregates(cls, academic_period_id: int) -> dict:
        """Agregados de métricas (snapshots) para un período."""
        qs = StudentFeatureSnapshot.objects.filter(
            academic_period_id=academic_period_id
        )
        agg = qs.aggregate(
            attendance_rate_avg=Avg("attendance_rate"),
            formative_avg=Avg("formative_avg_normalized"),
            summative_avg=Avg("summative_avg_normalized"),
            avg_severe_incidents=Avg("severe_incidents_count"),
        )
        return {
            "total_students": qs.count(),
            "failing_count": qs.filter(failing_subjects_count__gte=1).count(),
            "attendance_rate_avg": agg["attendance_rate_avg"] or 0,
            "formative_avg": agg["formative_avg"] or 0,
            "summative_avg": agg["summative_avg"] or 0,
            "avg_severe_incidents": agg["avg_severe_incidents"] or 0,
        }

    @classmethod
    def get_risk_label_counts(cls, academic_period_id: int) -> dict:
        """Distribución global de etiquetas de riesgo para un período."""
        return cls._label_counts(
            StudentRiskScore.objects.filter(academic_period_id=academic_period_id)
        )

    @classmethod
    def get_active_alerts_count(cls, academic_period_id: int) -> int:
        """Conteo de alertas tempranas no atendidas del período."""
        return EarlyAlert.objects.filter(
            academic_period_id=academic_period_id, attended=False
        ).count()

    @classmethod
    def scores_with_grade(cls, academic_period_id: int):
        return StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment__section__academic_grade")

    @classmethod
    def scores_with_city(cls, academic_period_id: int):
        return StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment__student__user__person__parish__city")

    @classmethod
    def scores_with_parish(cls, academic_period_id: int):
        return StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment__student__user__person__parish")

    @classmethod
    def scores_with_special_needs(cls, academic_period_id: int):
        return StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment__student__special_needs_type")

    @classmethod
    def scores_with_person_by_label(cls, academic_period_id: int, risk_label: str):
        return StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id, risk_label=risk_label
        ).select_related("enrollment__student__user__person")

    # ── Sección ──────────────────────────────────────────────────────────────
    @classmethod
    def get_section_snapshot_aggregates(
        cls, section_id: int, academic_period_id: int | None = None
    ) -> dict:
        qs = StudentFeatureSnapshot.objects.filter(enrollment__section_id=section_id)
        if academic_period_id is not None:
            qs = qs.filter(academic_period_id=academic_period_id)
        agg = qs.aggregate(
            attendance_rate_avg=Avg("attendance_rate"),
            formative_avg=Avg("formative_avg_normalized"),
        )
        return {
            "total_students": qs.count(),
            "attendance_rate_avg": agg["attendance_rate_avg"] or 0,
            "formative_avg": agg["formative_avg"] or 0,
        }

    @classmethod
    def get_section_risk_label_counts(
        cls, section_id: int, academic_period_id: int | None = None
    ) -> dict:
        qs = StudentRiskScore.objects.filter(enrollment__section_id=section_id)
        if academic_period_id is not None:
            qs = qs.filter(academic_period_id=academic_period_id)
        return cls._label_counts(qs)

    # ── Matrículas: deserción / retiro / tendencia ───────────────────────────
    @classmethod
    def enrollments_with_city(cls, school_year_id: Optional[int] = None):
        qs = Enrollment.objects.select_related("student__user__person__city")
        if school_year_id:
            qs = qs.filter(section__school_year_id=school_year_id)
        return qs

    @classmethod
    def withdrawn_enrollments_with_reason(cls, school_year_id: Optional[int] = None):
        qs = Enrollment.objects.filter(enrollment_status="RET").select_related(
            "withdrawal_reason"
        )
        if school_year_id:
            qs = qs.filter(section__school_year_id=school_year_id)
        return qs

    @classmethod
    def get_enrollment_trend_rows(cls, school_year_id: Optional[int] = None):
        """
        Tendencia de matrículas acumuladas por año lectivo.
        
        Si school_year_id es None, devuelve todos los años lectivos.
        Útil para comparar años lectivos entre sí.
        """
        from apps.institutions.school_year.infrastructure.models import SchoolYear
        
        qs = Enrollment.objects.select_related("section__school_year").all()
        
        if school_year_id:
            qs = qs.filter(section__school_year_id=school_year_id)
        
        # Agrupar por año lectivo y fecha de matrícula
        return (
            qs.annotate(
                school_year_start=TruncMonth("section__school_year__start_date"),
                enrollment_month=TruncMonth("enrollment_date")
            )
            .values("school_year_start", "enrollment_month")
            .annotate(count=Count("id"))
            .order_by("school_year_start", "enrollment_month")
        )

    @classmethod
    def get_enrollment_comparison_by_school_year(cls) -> list:
        """
        Comparativa de matrículas entre años lectivos.
        
        Devuelve el total de matrículas por año lectivo para poder comparar.
        """
        from apps.institutions.school_year.infrastructure.models import SchoolYear
        
        return list(
            Enrollment.objects.select_related("section__school_year")
            .values(
                "section__school_year__id",
                "section__school_year__start_date",
                "section__school_year__end_date",
            )
            .annotate(total_enrollments=Count("id"))
            .order_by("section__school_year__start_date")
        )

    @classmethod
    def get_enrollment_cumulative_by_school_year(cls, school_year_id: int) -> list:
        """
        Evolución acumulada de matrículas dentro de un año lectivo.
        
        Muestra cómo crece el número de matrículas a lo largo del tiempo
        desde el inicio del año lectivo.
        """
        qs = Enrollment.objects.filter(
            section__school_year_id=school_year_id
        ).order_by("enrollment_date")
        
        cumulative_count = 0
        result = []
        
        for enrollment in qs:
            cumulative_count += 1
            result.append({
                "date": enrollment.enrollment_date.isoformat(),
                "cumulative_count": cumulative_count,
                "month": enrollment.enrollment_date.strftime("%Y-%m"),
            })
        
        return result

    @classmethod
    def get_active_student_ids_for_period(cls, academic_period_id: int) -> list:
        return list(
            Enrollment.objects.filter(
                enrollment_status="ACT",
                section__school_year__academic_periods__id=academic_period_id,
            ).values_list("student_id", flat=True)
        )

    # ── Exportación CSV ──────────────────────────────────────────────────────
    @classmethod
    def get_risk_export_rows(cls, academic_period_id: int):
        return StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).values_list(
            "enrollment__student__student_code", "risk_score", "risk_label"
        )

    @classmethod
    def get_attendance_export_rows(cls, academic_period_id: int):
        return StudentFeatureSnapshot.objects.filter(
            academic_period_id=academic_period_id
        ).values_list(
            "enrollment__student__student_code", "attendance_rate", "tardiness_count"
        )

    # ── Director Dashboard ──────────────────────────────────────────────────
    @classmethod
    def get_failing_subjects_ranking(cls, academic_period_id: int, limit: int = 5) -> list:
        """Materias con mayor tasa de fracaso en el período."""
        qs = (
            PeriodGradeSummary.objects.filter(academic_period_id=academic_period_id)
            .values("subject_offering__subject_academic_config__subject__name")
            .annotate(
                total=Count("id"),
                fail_count=Count("id", filter=Q(is_failing=True)),
            )
            .order_by("-fail_count")[:limit]
        )
        return [
            {
                "subject": r["subject_offering__subject_academic_config__subject__name"],
                "fail_count": r["fail_count"],
                "total": r["total"],
                "fail_rate": round(r["fail_count"] / r["total"] * 100, 1) if r["total"] else 0,
            }
            for r in qs
        ]

    @classmethod
    def get_unattended_alerts_summary(cls, academic_period_id: int) -> dict:
        """Conteo de alertas no atendidas agrupadas por nivel de urgencia."""
        qs = EarlyAlert.objects.filter(
            academic_period_id=academic_period_id, attended=False
        )
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for row in qs.values("urgency_level").annotate(n=Count("id")):
            if row["urgency_level"] in counts:
                counts[row["urgency_level"]] = row["n"]
        return counts

    @classmethod
    def get_declining_students(cls, academic_period_id: int, limit: int = 5) -> list:
        """Estudiantes con tendencia descendente más pronunciada (grade_trend_slope)."""
        qs = (
            StudentFeatureSnapshot.objects.filter(academic_period_id=academic_period_id)
            .exclude(grade_trend_slope__isnull=True)
            .order_by("grade_trend_slope")
            .select_related("enrollment__student__user__person")[:limit]
        )
        return [
            {
                "student_id": s.enrollment.student_id,
                "student_name": str(s.enrollment.student.user.person),
                "grade_trend_slope": float(s.grade_trend_slope),
            }
            for s in qs
        ]

    @classmethod
    def get_near_threshold_students(cls, academic_period_id: int) -> dict:
        """
        Estudiantes cerca del umbral de cambio de semáforo.

        Los umbrales se leen desde EffectiveScoringConfig (configurable via
        RiskScoringConfig). Se usa un buffer de 5 puntos para detectar
        estudiantes próximos a cambiar de nivel.
        """
        from apps.analytics.services.risk_scoring_config_service import (
            RiskScoringConfigService,
        )

        config = RiskScoringConfigService.get_effective()
        red_min = float(config.score_red_min)
        yellow_min = float(config.score_yellow_min)
        buffer = 5.0

        scores = StudentRiskScore.objects.filter(
            academic_period_id=academic_period_id
        ).select_related("enrollment__student__user__person")

        def _format(s):
            return {
                "student_id": s.enrollment.student_id,
                "student_name": str(s.enrollment.student.user.person),
                "risk_score": float(s.risk_score),
                "risk_label": s.risk_label,
            }

        yellow_to_red = [
            _format(s)
            for s in scores.filter(
                risk_score__gte=red_min - buffer, risk_score__lt=red_min
            )
        ]
        green_to_yellow = [
            _format(s)
            for s in scores.filter(
                risk_score__gte=yellow_min - buffer, risk_score__lt=yellow_min
            )
        ]

        return {
            "yellow_to_red": yellow_to_red,
            "green_to_yellow": green_to_yellow,
        }

    @classmethod
    def get_risk_factors_breakdown(cls, academic_period_id: int) -> list:
        """Peso promedio de contribución de cada factor de riesgo."""
        qs = (
            StudentRiskFactor.objects.filter(
                student_risk_score__academic_period_id=academic_period_id
            )
            .values("risk_factor__name")
            .annotate(avg_weight=Avg("contribution_weight"))
            .order_by("-avg_weight")
        )
        return [
            {"factor": r["risk_factor__name"], "avg_weight": float(r["avg_weight"])}
            for r in qs
        ]

    @classmethod
    def get_recent_incidents(cls, academic_period_id: int, limit: int = 5) -> list:
        """Últimos incidentes de conducta del período."""
        qs = (
            ConductIncident.objects.filter(academic_period_id=academic_period_id)
            .select_related(
                "enrollment__student__user__person",
                "incident_type",
                "severity",
            )
            .order_by("-incident_date")[:limit]
        )
        return [
            {
                "id": i.id,
                "student_name": str(i.enrollment.student.user.person),
                "incident_type": i.incident_type.name if i.incident_type else "—",
                "severity": i.severity.name if i.severity else "—",
                "incident_date": i.incident_date.isoformat(),
                "family_notified": i.family_notified,
            }
            for i in qs
        ]

    @classmethod
    def get_critical_alerts(cls, academic_period_id: int, limit: int = 5) -> list:
        """Alertas tempranas no atendidas más recientes."""
        qs = (
            EarlyAlert.objects.filter(
                academic_period_id=academic_period_id, attended=False
            )
            .select_related("enrollment__student__user__person")
            .order_by("-detected_at")[:limit]
        )
        return [
            {
                "id": a.id,
                "enrollment_name": str(a.enrollment.student.user.person),
                "description": a.description,
                "urgency_level": a.urgency_level,
                "detected_at": a.detected_at.isoformat(),
            }
            for a in qs
        ]

    @classmethod
    def get_special_needs_gap(cls, academic_period_id: int) -> dict:
        """Comparativa de rendimiento entre estudiantes con NEE y sin NEE."""
        qs = StudentFeatureSnapshot.objects.filter(
            academic_period_id=academic_period_id
        )

        def _stats(qs):
            agg = qs.aggregate(
                count=Count("id"),
                fail_count=Count("id", filter=Q(failing_subjects_count__gte=1)),
                avg_formative=Avg("formative_avg_normalized"),
            )
            fail_rate = round(agg["fail_count"] / agg["count"] * 100, 1) if agg["count"] else 0
            return {
                "count": agg["count"],
                "fail_rate": fail_rate,
                "avg_formative": float(agg["avg_formative"] or 0),
            }

        with_needs = _stats(qs.filter(has_special_needs=True))
        without_needs = _stats(qs.filter(has_special_needs=False))
        gap = round(with_needs["fail_rate"] - without_needs["fail_rate"], 1)

        return {
            "with_needs": with_needs,
            "without_needs": without_needs,
            "fail_rate_gap": gap,
        }

    # ── Teacher Dashboard ─────────────────────────────────────────────────

    @classmethod
    def _teacher_tss_qs(cls, user_id: int, academic_period_id: int):
        """TeacherSubjectSection del docente en el año escolar al que pertenece el período."""
        period = AcademicPeriod.objects.get(id=academic_period_id)
        return TeacherSubjectSection.objects.filter(
            user_id=user_id,
            is_active=True,
            subject_offering__section__school_year=period.school_year,
        )

    @classmethod
    def _teacher_section_ids(cls, user_id: int, academic_period_id: int) -> list:
        """IDs únicos de secciones que el docente enseña en el período."""
        return list(
            cls._teacher_tss_qs(user_id, academic_period_id)
            .values_list("subject_offering__section_id", flat=True)
            .distinct()
        )

    @classmethod
    def _teacher_tss_ids(cls, user_id: int, academic_period_id: int) -> list:
        """IDs de las asignaciones TeacherSubjectSection del docente."""
        return list(
            cls._teacher_tss_qs(user_id, academic_period_id)
            .values_list("id", flat=True)
        )

    @classmethod
    def _teacher_filter(cls, qs, user_id: int, academic_period_id: int):
        """Helper: filtra un queryset por las secciones del docente."""
        section_ids = cls._teacher_section_ids(user_id, academic_period_id)
        return qs.filter(enrollment__section_id__in=section_ids) if section_ids else qs.none()

    @classmethod
    def get_teacher_overview(cls, user_id: int, academic_period_id: int) -> dict:
        """Resumen de métricas del docente (estudiantes, asistencia, formativo)."""
        qs = cls._teacher_filter(
            StudentFeatureSnapshot.objects.filter(academic_period_id=academic_period_id),
            user_id,
            academic_period_id,
        )
        agg = qs.aggregate(
            attendance_rate_avg=Avg("attendance_rate"),
            formative_avg=Avg("formative_avg_normalized"),
        )
        return {
            "total_students": qs.count(),
            "attendance_rate_avg": agg["attendance_rate_avg"] or 0,
            "formative_avg": agg["formative_avg"] or 0,
        }

    @classmethod
    def get_teacher_active_alerts_count(cls, user_id: int, academic_period_id: int) -> int:
        """Alertas no atendidas de los estudiantes del docente."""
        return cls._teacher_filter(
            EarlyAlert.objects.filter(academic_period_id=academic_period_id, attended=False),
            user_id,
            academic_period_id,
        ).count()

    @classmethod
    def get_teacher_sections_performance(cls, user_id: int, academic_period_id: int) -> list:
        """Resumen por sección/materia que el docente enseña."""
        tss_qs = cls._teacher_tss_qs(user_id, academic_period_id).select_related(
            "subject_offering__section__academic_grade",
            "subject_offering__subject_academic_config__subject",
        )
        seen = set()
        result = []
        for tss in tss_qs:
            section = tss.subject_offering.section
            section_id = section.id
            if section_id in seen:
                continue
            seen.add(section_id)
            section_name = f"{section.academic_grade.name} {section.parallel}".strip()
            subject_name = tss.subject_offering.subject_academic_config.subject.name

            metrics = cls.get_section_snapshot_aggregates(section_id, academic_period_id)
            risk = cls.get_section_risk_label_counts(section_id, academic_period_id)

            # Count pending grading for this section
            pending = cls._count_section_pending_grading(
                section_id, tss.id, academic_period_id
            )

            result.append({
                "section_id": section_id,
                "section_name": section_name,
                "subject": subject_name,
                "total_students": metrics["total_students"],
                "attendance_rate_avg": metrics["attendance_rate_avg"] or 0,
                "formative_avg": metrics["formative_avg"] or 0,
                "risk_distribution": risk,
                "pending_grading": pending,
            })
        return result

    @classmethod
    def _count_section_pending_grading(
        cls, section_id: int, tss_id: int, academic_period_id: int
    ) -> int:
        """Cuenta actividades activas del período para esta sección que aún tienen
        estudiantes sin nota."""
        period = AcademicPeriod.objects.only("start_date", "end_date").get(
            id=academic_period_id
        )
        activities = EvaluativeActivity.objects.filter(
            teacher_subject_section_id=tss_id,
            is_active=True,
            due_date__gte=period.start_date,
            due_date__lte=period.end_date,
        )
        total_pending = 0
        for act in activities:
            enrolled = Enrollment.objects.filter(
                section_id=section_id, enrollment_status="ACT"
            ).count()
            graded = StudentNote.objects.filter(
                evaluative_activity=act
            ).count()
            total_pending += max(0, enrolled - graded)
        return total_pending

    @classmethod
    def get_teacher_pending_grading(
        cls, user_id: int, academic_period_id: int, limit: int = 10
    ) -> list:
        """Actividades del período con estudiantes pendientes de calificar."""
        tss_ids = cls._teacher_tss_ids(user_id, academic_period_id)
        if not tss_ids:
            return []

        period = AcademicPeriod.objects.only("start_date", "end_date").get(
            id=academic_period_id
        )

        activities = EvaluativeActivity.objects.filter(
            teacher_subject_section_id__in=tss_ids,
            is_active=True,
            due_date__gte=period.start_date,
            due_date__lte=period.end_date,
        ).select_related(
            "teacher_subject_section__subject_offering__section__academic_grade",
            "teacher_subject_section__subject_offering__subject_academic_config__subject",
        ).order_by("-due_date")[:limit]

        result = []
        for act in activities:
            section = act.teacher_subject_section.subject_offering.section
            section_name = f"{section.academic_grade.name} {section.parallel}".strip()
            subject_name = (
                act.teacher_subject_section.subject_offering
                .subject_academic_config.subject.name
            )
            total_enrolled = Enrollment.objects.filter(
                section_id=section.id, enrollment_status="ACT"
            ).count()
            graded = StudentNote.objects.filter(evaluative_activity=act).count()
            pending = max(0, total_enrolled - graded)

            if pending > 0:
                result.append({
                    "activity_id": act.id,
                    "title": act.title,
                    "section_name": section_name,
                    "subject": subject_name,
                    "total_students": total_enrolled,
                    "graded": graded,
                    "pending": pending,
                    "due_date": act.due_date.isoformat(),
                })
        return result

    @classmethod
    def get_teacher_upcoming_activities(
        cls, user_id: int, academic_period_id: int, limit: int = 5
    ) -> list:
        """Próximas actividades del docente dentro del período actual."""
        tss_ids = cls._teacher_tss_ids(user_id, academic_period_id)
        if not tss_ids:
            return []

        from django.utils import timezone

        period = AcademicPeriod.objects.only("end_date").get(
            id=academic_period_id
        )
        today = timezone.now().date()

        activities = EvaluativeActivity.objects.filter(
            teacher_subject_section_id__in=tss_ids,
            is_active=True,
            due_date__gte=today,
            due_date__lte=period.end_date,
        ).select_related(
            "teacher_subject_section__subject_offering__section__academic_grade",
            "teacher_subject_section__subject_offering__subject_academic_config__subject",
            "activity_type",
        ).order_by("due_date")[:limit]

        return [
            {
                "activity_id": a.id,
                "title": a.title,
                "type": a.activity_type.name if a.activity_type else "Actividad",
                "section_name": (
                    f"{a.teacher_subject_section.subject_offering.section.academic_grade.name} "
                    f"{a.teacher_subject_section.subject_offering.section.parallel}"
                ).strip(),
                "subject": (
                    a.teacher_subject_section.subject_offering
                    .subject_academic_config.subject.name
                ),
                "due_date": a.due_date.isoformat(),
            }
            for a in activities
        ]

    @classmethod
    def get_teacher_risk_distribution(cls, user_id: int, academic_period_id: int) -> dict:
        """Distribución de riesgo de los estudiantes del docente."""
        qs = cls._teacher_filter(
            StudentRiskScore.objects.filter(academic_period_id=academic_period_id),
            user_id,
            academic_period_id,
        )
        return cls._label_counts(qs)

    @classmethod
    def get_teacher_declining_students(
        cls, user_id: int, academic_period_id: int, limit: int = 5
    ) -> list:
        """Estudiantes con tendencia descendente (secciones del docente)."""
        qs = cls._teacher_filter(
            StudentFeatureSnapshot.objects.filter(academic_period_id=academic_period_id)
            .exclude(grade_trend_slope__isnull=True)
            .select_related("enrollment__student__user__person"),
            user_id,
            academic_period_id,
        ).order_by("grade_trend_slope")[:limit]
        return [
            {
                "student_id": s.enrollment.student_id,
                "student_name": str(s.enrollment.student.user.person),
                "grade_trend_slope": float(s.grade_trend_slope),
                "section": s.enrollment.section.academic_grade.name + " " + s.enrollment.section.parallel,
            }
            for s in qs
        ]

    @classmethod
    def get_teacher_critical_alerts(
        cls, user_id: int, academic_period_id: int, limit: int = 5
    ) -> list:
        """Alertas críticas no atendidas de estudiantes del docente."""
        qs = cls._teacher_filter(
            EarlyAlert.objects.filter(academic_period_id=academic_period_id, attended=False)
            .select_related("enrollment__section__academic_grade", "enrollment__student__user__person")
            .order_by("-detected_at"),
            user_id,
            academic_period_id,
        )[:limit]
        return [
            {
                "id": a.id,
                "enrollment_name": str(a.enrollment.student.user.person),
                "description": a.description,
                "urgency_level": a.urgency_level,
                "section": a.enrollment.section.academic_grade.name + " " + a.enrollment.section.parallel,
                "detected_at": a.detected_at.isoformat(),
            }
            for a in qs
        ]

    @classmethod
    def get_teacher_students_near_threshold(
        cls, user_id: int, academic_period_id: int, limit: int = 5
    ) -> list:
        """Estudiantes más cerca de empeorar su semáforo (secciones del docente)."""
        from apps.analytics.services.risk_scoring_config_service import (
            RiskScoringConfigService,
        )

        config = RiskScoringConfigService.get_effective()
        yellow_min = float(config.score_yellow_min)

        qs = cls._teacher_filter(
            StudentRiskScore.objects.filter(academic_period_id=academic_period_id)
            .select_related("enrollment__student__user__person", "enrollment__section__academic_grade"),
            user_id,
            academic_period_id,
        ).filter(risk_score__gte=yellow_min - 5)

        scores = list(qs.order_by("-risk_score")[:limit])
        return [
            {
                "student_id": s.enrollment.student_id,
                "student_name": str(s.enrollment.student.user.person),
                "risk_score": float(s.risk_score),
                "risk_label": s.risk_label,
                "section": s.enrollment.section.academic_grade.name + " " + s.enrollment.section.parallel,
            }
            for s in scores
        ]
