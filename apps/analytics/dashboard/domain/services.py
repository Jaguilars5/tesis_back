"""
Servicios de dominio para dashboard y reportes analíticos.

Agrupa métricas y datos para visualizaciones. Todo el acceso a datos se delega a
``DashboardRepository`` (checklist §5: sin ``Model.objects`` ni imports de modelos
de otras apps en la capa de servicio).
"""

import csv
import io
from typing import Any, Dict, List, Optional

from ..infrastructure.repositories import DashboardRepository


class DashboardService:
    """
    Servicio para métricas y KPIs del dashboard analítico.

    Proporciona agregaciones sobre datos de riesgo, asistencia y conducta.
    """

    repository = DashboardRepository

    @classmethod
    def get_overview(cls, academic_period_id: int) -> Dict[str, Any]:
        """KPIs globales para un período académico."""
        metrics = cls.repository.get_snapshot_aggregates(academic_period_id)
        return {
            "period_id": academic_period_id,
            "total_students": metrics["total_students"],
            "attendance_rate_avg": metrics["attendance_rate_avg"],
            "formative_avg": metrics["formative_avg"],
            "summative_avg": metrics["summative_avg"],
            "failing_count": metrics["failing_count"],
            "risk_distribution": cls.repository.get_risk_label_counts(
                academic_period_id
            ),
            "active_alerts": cls.repository.get_active_alerts_count(academic_period_id),
            "avg_severe_incidents": metrics["avg_severe_incidents"],
        }

    @classmethod
    def get_risk_distribution_by_grade(cls, academic_period_id: int) -> Dict[str, Dict]:
        """Distribución de riesgo por grado académico."""

        def grade_name(score):
            return score.enrollment.section.academic_grade.name

        return cls._risk_distribution_by_dimension(
            cls.repository.scores_with_grade(academic_period_id), grade_name
        )

    @classmethod
    def _risk_distribution_by_dimension(
        cls, scores, key_fn
    ) -> Dict[str, Dict[str, int]]:
        """Helper para distribución por dimensión arbitraria."""
        distribution: Dict[str, Dict[str, int]] = {}
        for score in scores:
            key = key_fn(score) or "Sin asignar"
            bucket = distribution.setdefault(
                key, {"rojo": 0, "amarillo": 0, "verde": 0, "total": 0}
            )
            if score.risk_label in bucket:
                bucket[score.risk_label] += 1
            bucket["total"] += 1
        return distribution

    @classmethod
    def get_risk_distribution_by_city(cls, academic_period_id: int) -> Dict[str, Dict]:
        """Distribución de riesgo por ciudad de origen."""

        def city_name(score):
            person = getattr(score.enrollment.student.user, "person", None)
            parish = getattr(person, "parish", None) if person else None
            city = getattr(parish, "city", None) if parish else None
            return city.name if city else None

        return cls._risk_distribution_by_dimension(
            cls.repository.scores_with_city(academic_period_id), city_name
        )

    @classmethod
    def get_risk_distribution_by_parish(cls, academic_period_id: int) -> Dict[str, Dict]:
        """Distribución de riesgo por parroquia de origen."""

        def parish_name(score):
            person = getattr(score.enrollment.student.user, "person", None)
            parish = getattr(person, "parish", None) if person else None
            return parish.name if parish else None

        return cls._risk_distribution_by_dimension(
            cls.repository.scores_with_parish(academic_period_id), parish_name
        )

    @classmethod
    def get_risk_distribution_by_special_needs_type(
        cls, academic_period_id: int
    ) -> Dict[str, Dict]:
        """Distribución de riesgo por tipo de NEE (Fase 4)."""

        def needs_type(score):
            snt = score.enrollment.student.special_needs_type
            return snt.name if snt else "Sin NEE"

        return cls._risk_distribution_by_dimension(
            cls.repository.scores_with_special_needs(academic_period_id), needs_type
        )

    @classmethod
    def get_dropout_by_city(
        cls, school_year_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Índice de deserción por ciudad.

        Retorna lista de dicts con ciudad, total, retirados y tasa.
        """
        rows: Dict[str, Dict[str, int]] = {}
        for enrollment in cls.repository.enrollments_with_city(school_year_id):
            person = getattr(enrollment.student.user, "person", None)
            city = getattr(person, "city", None) if person else None
            name = city.name if city else "Sin asignar"
            bucket = rows.setdefault(name, {"total": 0, "withdrawn": 0})
            bucket["total"] += 1
            if enrollment.enrollment_status == "RET":
                bucket["withdrawn"] += 1

        return [
            {
                "city": name,
                "total": data["total"],
                "withdrawn": data["withdrawn"],
                "dropout_rate": (
                    round(data["withdrawn"] / data["total"], 4) if data["total"] else 0.0
                ),
            }
            for name, data in sorted(
                rows.items(), key=lambda kv: kv[1]["withdrawn"], reverse=True
            )
        ]

    @classmethod
    def get_withdrawal_reasons(
        cls, school_year_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Conteo de motivos de retiro."""
        counts: Dict[str, int] = {}
        for enrollment in cls.repository.withdrawn_enrollments_with_reason(
            school_year_id
        ):
            reason = enrollment.withdrawal_reason
            name = reason.name if reason else "Sin especificar"
            counts[name] = counts.get(name, 0) + 1

        return [
            {"reason": name, "count": count}
            for name, count in sorted(
                counts.items(), key=lambda kv: kv[1], reverse=True
            )
        ]

    @classmethod
    def get_students_at_risk(
        cls, academic_period_id: int, risk_label: str = "rojo"
    ) -> List[Dict[str, Any]]:
        """Lista de estudiantes con nivel de riesgo específico."""
        return [
            {
                "student_id": s.enrollment.student_id,
                "student_name": str(s.enrollment.student.user.person),
                "risk_score": float(s.risk_score),
                "risk_label": s.risk_label,
            }
            for s in cls.repository.scores_with_person_by_label(
                academic_period_id, risk_label
            )
        ]

    @classmethod
    def get_section_summary(cls, section_id: int) -> Dict[str, Any]:
        """Resumen de métricas para una sección específica."""
        metrics = cls.repository.get_section_snapshot_aggregates(section_id)
        return {
            "section_id": section_id,
            "total_students": metrics["total_students"],
            "attendance_rate_avg": metrics["attendance_rate_avg"],
            "formative_avg": metrics["formative_avg"],
            "risk_distribution": cls.repository.get_section_risk_label_counts(
                section_id
            ),
        }

    @classmethod
    def get_enrollment_trend(
        cls, school_year_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Tendencia de matrículas por mes."""
        return [
            {"month": r["month"].strftime("%Y-%m"), "count": r["count"]}
            for r in cls.repository.get_enrollment_trend_rows(school_year_id)
            if r["month"] is not None
        ]

    @classmethod
    def get_enrollment_comparison(cls) -> List[Dict[str, Any]]:
        """
        Comparativa de matrículas entre años lectivos.
        
        Devuelve lista de años lectivos con su total de matrículas.
        """
        return [
            {
                "school_year_id": r["section__school_year__id"],
                "start_date": r["section__school_year__start_date"].isoformat(),
                "end_date": r["section__school_year__end_date"].isoformat(),
                "name": f"{r['section__school_year__start_date'].year}-{r['section__school_year__end_date'].year}",
                "total_enrollments": r["total_enrollments"],
            }
            for r in cls.repository.get_enrollment_comparison_by_school_year()
        ]

    @classmethod
    def get_enrollment_cumulative(cls, school_year_id: int) -> List[Dict[str, Any]]:
        """
        Evolución acumulada de matrículas dentro de un año lectivo.
        """
        return cls.repository.get_enrollment_cumulative_by_school_year(school_year_id)


class TeacherDashboardService:
    """
    Servicio que consolida las métricas del docente en una sola respuesta,
    enfocada en actividades sin calificar, próximas actividades, rendimiento
    de sus cursos, y estudiantes que requieren atención.
    """

    repository = DashboardRepository

    @classmethod
    def get_teacher_dashboard(
        cls,
        user_id: int,
        academic_period_id: int,
    ) -> Dict[str, Any]:
        """
        Respuesta unificada del dashboard del docente.

        Args:
            user_id: ID del usuario docente.
            academic_period_id: período activo.

        Returns:
            Dict con datos orientados a la gestión del aula.
        """
        repo = cls.repository
        data: Dict[str, Any] = {}

        # ── Core: resumen general ──
        try:
            overview = repo.get_teacher_overview(user_id, academic_period_id)
            data["total_students"] = overview["total_students"]
            data["attendance_rate_avg"] = overview["attendance_rate_avg"]
            data["formative_avg"] = overview["formative_avg"]
        except Exception:
            data["total_students"] = 0
            data["attendance_rate_avg"] = 0
            data["formative_avg"] = 0

        try:
            data["active_alerts"] = repo.get_teacher_active_alerts_count(
                user_id, academic_period_id
            )
        except Exception:
            data["active_alerts"] = 0

        try:
            data["courses_count"] = len(
                repo.get_teacher_sections_performance(user_id, academic_period_id)
            )
        except Exception:
            data["courses_count"] = 0

        # ── Secciones ──
        try:
            data["sections_performance"] = repo.get_teacher_sections_performance(
                user_id, academic_period_id
            )
        except Exception:
            data["sections_performance"] = []

        # ── Actividades sin calificar ──
        try:
            data["pending_grading"] = repo.get_teacher_pending_grading(
                user_id, academic_period_id
            )
        except Exception:
            data["pending_grading"] = []

        # ── Próximas actividades ──
        try:
            data["upcoming_activities"] = repo.get_teacher_upcoming_activities(
                user_id, academic_period_id
            )
        except Exception:
            data["upcoming_activities"] = []

        # ── Riesgo ──
        try:
            data["risk_distribution"] = repo.get_teacher_risk_distribution(
                user_id, academic_period_id
            )
        except Exception:
            data["risk_distribution"] = {"rojo": 0, "amarillo": 0, "verde": 0}

        # ── Estudiantes en declive ──
        try:
            data["declining_students"] = repo.get_teacher_declining_students(
                user_id, academic_period_id
            )
        except Exception:
            data["declining_students"] = []

        # ── Alertas críticas ──
        try:
            data["critical_alerts"] = repo.get_teacher_critical_alerts(
                user_id, academic_period_id
            )
        except Exception:
            data["critical_alerts"] = []

        # ── Estudiantes cerca del umbral ──
        try:
            data["students_near_threshold"] = repo.get_teacher_students_near_threshold(
                user_id, academic_period_id
            )
        except Exception:
            data["students_near_threshold"] = []

        return data


class CSVExportService:
    """
    Servicio para exportación de datos a CSV.
    """

    EXPORT_TYPES = {
        "risk": {
            "rows_method": "get_risk_export_rows",
            "headers": ["Código Estudiante", "Score Riesgo", "Nivel"],
        },
        "attendance": {
            "rows_method": "get_attendance_export_rows",
            "headers": ["Código Estudiante", "% Asistencia", "Tardanzas"],
        },
    }

    repository = DashboardRepository

    @classmethod
    def generate_csv(cls, export_type: str, academic_period_id: int) -> str:
        """
        Genera CSV para el tipo de exportación especificado.

        Args:
            export_type: "risk" o "attendance"
            academic_period_id: ID del período académico

        Returns:
            String con contenido CSV
        """
        config = cls.EXPORT_TYPES.get(export_type)
        if not config:
            raise ValueError(f"Tipo de exportación no válido: {export_type}")

        rows = getattr(cls.repository, config["rows_method"])(academic_period_id)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(config["headers"])
        for row in rows:
            writer.writerow(row)

        return output.getvalue()


class RecalculationService:
    """
    Servicio para recalcular riesgo de estudiantes.
    """

    repository = DashboardRepository

    @classmethod
    def get_student_ids_for_period(cls, academic_period_id: int) -> List[int]:
        """Obtiene IDs de estudiantes activos para un período."""
        return cls.repository.get_active_student_ids_for_period(academic_period_id)

    @classmethod
    def recalculate_period(cls, academic_period_id: int, user_id: Optional[int] = None):
        """
        Inicia recálculo de riesgo para todos los estudiantes de un período.

        Retorna el task de Celery iniciado.
        """
        from apps.analytics.student_risk.domain.services import (
            StudentRiskCalculationService,
        )

        student_ids = cls.get_student_ids_for_period(academic_period_id)
        if not student_ids:
            return None

        return StudentRiskCalculationService.batch_calculate(
            academic_period_id, student_ids, user_id=user_id
        )


class DirectorDashboardService:
    """
    Servicio que consolida todas las métricas del director en una sola
    respuesta, delegando cada consulta al repositorio.

    Sigue el mismo patrón que DashboardService pero orquesta múltiples
    fuentes de datos para evitar N llamadas desde el frontend.
    """

    repository = DashboardRepository

    # ── Secciones "core" (siempre incluidas) ──────────────────────────────

    SECTIONS = {
        "overview": lambda repo, pid, **_kw: DashboardService.get_overview(pid),
        "risk_by_grade": lambda repo, pid, **_kw: DashboardService.get_risk_distribution_by_grade(pid),
        "enrollment_trend": lambda repo, pid, **kw: DashboardService.get_enrollment_trend(kw.get("school_year_id")),
        "failing_subjects": lambda repo, pid, **_kw: repo.get_failing_subjects_ranking(pid),
        "unattended_alerts_summary": lambda repo, pid, **_kw: repo.get_unattended_alerts_summary(pid),
        "risk_factor_breakdown": lambda repo, pid, **_kw: repo.get_risk_factors_breakdown(pid),
        "declining_students": lambda repo, pid, **_kw: repo.get_declining_students(pid),
        "near_threshold": lambda repo, pid, **_kw: repo.get_near_threshold_students(pid),
        "critical_alerts": lambda repo, pid, **_kw: repo.get_critical_alerts(pid),
        "recent_incidents": lambda repo, pid, **_kw: repo.get_recent_incidents(pid),
    }

    # ── Secciones "opt-in" (solo si se solicitan) ─────────────────────────
    OPTIONAL_SECTIONS = {
        "risk_by_city": lambda repo, pid, **_kw: DashboardService.get_risk_distribution_by_city(pid),
        "risk_by_parish": lambda repo, pid, **_kw: DashboardService.get_risk_distribution_by_parish(pid),
        "special_needs_gap": lambda repo, pid, **_kw: repo.get_special_needs_gap(pid),
    }

    @classmethod
    def get_director_dashboard(
        cls,
        academic_period_id: int,
        school_year_id: Optional[int] = None,
        include_risk_by_city: bool = False,
        include_risk_by_parish: bool = False,
        include_special_needs_gap: bool = False,
    ) -> Dict[str, Any]:
        """
        Respuesta unificada del dashboard del director.

        Args:
            academic_period_id: período activo.
            school_year_id: año escolar (opcional, para tendencia de matrículas).
            include_risk_by_city: incluir distribución por ciudad.
            include_special_needs_gap: incluir brecha NEE.

        Returns:
            Dict con todas las secciones solicitadas.
        """
        data: Dict[str, Any] = {}
        kw = {"school_year_id": school_year_id}

        # Core sections
        for name, loader in cls.SECTIONS.items():
            try:
                data[name] = loader(cls.repository, academic_period_id, **kw)
            except Exception as exc:
                data[name] = None

        # Merge overview keys at top level for backward compatibility
        overview = data.pop("overview", {}) or {}
        data.update(overview)

        # Optional sections
        if include_risk_by_city:
            try:
                data["risk_by_city"] = cls.OPTIONAL_SECTIONS["risk_by_city"](
                    cls.repository, academic_period_id
                )
            except Exception:
                data["risk_by_city"] = None

        if include_risk_by_parish:
            try:
                data["risk_by_parish"] = cls.OPTIONAL_SECTIONS["risk_by_parish"](
                    cls.repository, academic_period_id
                )
            except Exception:
                data["risk_by_parish"] = None

        if include_special_needs_gap:
            try:
                data["special_needs_gap"] = cls.OPTIONAL_SECTIONS["special_needs_gap"](
                    cls.repository, academic_period_id
                )
            except Exception:
                data["special_needs_gap"] = None

        return data
