"""
Celery tasks para cálculo asíncrono de riesgo académico.

El motor de cálculo (reglas + ML) vive en
``apps.analytics.student_risk.domain.risk_engine`` (fuente única). Este módulo
sólo orquesta la ejecución asíncrona y la persistencia, y re-exporta las
funciones del motor por compatibilidad con código/tests existentes.
"""

import logging

from celery import shared_task
from django.db import transaction

from apps.core.realtime.emitter import emit_to_user
from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder
from apps.analytics.student_risk.domain import risk_engine
from apps.analytics.student_risk.domain.risk_engine import (  # noqa: F401  (re-export)
    MODEL_VERSION_FALLBACK,
    MODEL_VERSION_SKLEARN,
    _critical_factors,
    _detail_by_variable,
    _fallback_risk_score,
    _feature_vector,
    _predict_ml_score,
    _public_analysis,
    _risk_level,
)
from apps.analytics.ml.features import MODEL_PATH  # noqa: F401  (re-export)
from apps.analytics.student_risk.infrastructure.repositories import (
    RiskFactorRepository,
    StudentFeatureSnapshotRepository,
    StudentRiskFactorRepository,
    StudentRiskScoreRepository,
)

logger = logging.getLogger(__name__)

# Pesos por defecto (baseline Fase 0). El cálculo productivo usa la configuración
# efectiva (BD o defaults); se conserva como constante para baseline/tests.
WEIGHTS = {
    "conducta": 0.30,
    "asistencia": 0.35,
    "calificaciones": 0.35,
}

_model_available = MODEL_PATH.exists()


def calculate_academic_risk(snapshot, metrics=None):
    """Wrapper de compatibilidad sobre el motor de reglas/ML del módulo."""
    return risk_engine.calculate_risk(snapshot, metrics)


@shared_task(bind=True)
def calculate_student_academic_risk_task(self, student_id, academic_period_id, user_id=None):
    """
    Construye el snapshot, calcula el riesgo académico, persiste y retorna JSON.
    """
    task_id = getattr(self.request, "id", None)
    logger.info(
        "Iniciando cálculo de riesgo student_id=%s academic_period_id=%s task_id=%s",
        student_id,
        academic_period_id,
        task_id,
    )

    try:
        builder = AcademicRiskFeatureBuilder(student_id, academic_period_id)
        snapshot = builder.build()
        metrics = builder.build_persistence_metrics(snapshot)
        analysis = calculate_academic_risk(snapshot, metrics)

        with transaction.atomic():
            StudentFeatureSnapshotRepository.create_snapshot(
                student_id=student_id,
                academic_period_id=academic_period_id,
                metrics=metrics,
            )
            risk_score = StudentRiskScoreRepository.create_score(
                student_id=student_id,
                academic_period_id=academic_period_id,
                risk_score=analysis["semaforo_riesgo"]["puntaje_riesgo"],
                risk_label=analysis["semaforo_riesgo"]["nivel"],
                model_version=analysis["model_version"],
            )
            _populate_risk_factors(risk_score, analysis)

        logger.info(
            "Riesgo persistido student_id=%s period=%s modelo=%s nivel=%s score=%.2f task_id=%s",
            student_id,
            academic_period_id,
            analysis["model_version"],
            analysis["semaforo_riesgo"]["nivel"],
            analysis["semaforo_riesgo"]["puntaje_riesgo"],
            task_id,
        )
        return _public_analysis(analysis)
    except Exception:
        logger.exception(
            "Error en cálculo de riesgo student_id=%s academic_period_id=%s task_id=%s",
            student_id,
            academic_period_id,
            task_id,
        )
        raise


@shared_task(bind=True)
def batch_calculate_academic_risk(self, academic_period_id, student_ids, user_id=None):
    total = len(student_ids)
    results = {"total": total, "processed": 0, "failed": 0, "errors": []}

    for student_id in student_ids:
        try:
            calculate_student_academic_risk_task(student_id, academic_period_id)
            results["processed"] += 1
        except Exception as exc:
            results["failed"] += 1
            results["errors"].append({"student_id": student_id, "error": str(exc)})
            logger.error("Error calculando riesgo para estudiante %s: %s", student_id, exc)

    logger.info(
        "[BATCH] period_id=%s total=%d procesados=%d fallidos=%d modelo_disponible=%s task_id=%s",
        academic_period_id,
        total,
        results["processed"],
        results["failed"],
        _model_available,
        getattr(self.request, "id", None),
    )

    if user_id:
        emit_to_user(
            user_id,
            "task_completed",
            {"task_id": getattr(self.request, "id", None), "result": results},
        )

    return results


def _populate_risk_factors(risk_score, analysis):
    factor_mapping = {
        "LOW_ATTENDANCE": ("attendance_rate", 0.35),
        "FAILING_GRADES": ("failing_subjects_count", 0.35),
        "BEHAVIOR_ISSUES": ("severe_incidents_count", 0.20),
        "SOCIOEMOTIONAL": ("conduct_score", 0.10),
    }

    for factor_code, (variable_key, default_weight) in factor_mapping.items():
        factor = RiskFactorRepository.get_by_code(factor_code)
        if not factor:
            continue

        StudentRiskFactorRepository.model.objects.update_or_create(
            student_risk_score=risk_score,
            risk_factor=factor,
            defaults={"contribution_weight": default_weight},
        )


@shared_task(bind=True)
def auto_generate_early_alerts(self, period_id=None):
    from apps.academic.academic_period.infrastructure.repositories import (
        AcademicPeriodRepository,
    )
    from apps.analytics.early_alert.domain.services import EarlyAlertService
    from apps.students.repositories.enrollment_repo import EnrollmentRepository

    if not period_id:
        period = AcademicPeriodRepository.get_all(active_only=False).first()
        if not period:
            return {"error": "No active period found"}
        period_id = period.id

    enrollments = EnrollmentRepository.get_all()
    enrollments = [e for e in enrollments if e.enrollment_status == "ACT"]

    alerts_created = 0
    for enrollment in enrollments:
        period = AcademicPeriodRepository.get_by_id(period_id)
        alerts = EarlyAlertService.evaluate_student(enrollment, period)
        alerts_created += len(alerts)

    return {"processed": len(enrollments), "alerts_created": alerts_created}


@shared_task(bind=True)
def run_student_clustering(self, period_id=None):
    from apps.analytics.services.clustering_service import StudentClusteringService

    if not period_id:
        from apps.academic.academic_period import AcademicPeriod

        period = AcademicPeriod.objects.filter(is_active=True).first()
        if not period:
            return {"error": "No active period found"}
        period_id = period.id
    return StudentClusteringService.cluster_students(period_id)


@shared_task(bind=True)
def refresh_materialized_views(self):
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(
            "REFRESH MATERIALIZED VIEW CONCURRENTLY analytics_section_risk_summary"
        )
    return {"ok": True}
