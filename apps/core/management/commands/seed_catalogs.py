from django.core.management.base import BaseCommand

from apps.people.models import DocumentType
from apps.academic.models import PeriodType, Subject
from apps.grading.models import GradeType, QualitativeScale, ActivityType, EvaluationType, PromotionStatus, RecoveryProcessType
from apps.attendance.models import AttendanceStatus, AbsenceType
from apps.behavior.models import IncidentType, SocioemotionalSkill
from apps.analytics.models import AlertType, UrgencyLevel, RiskFactor
from apps.integration.models import SyncOperation, SyncStatus
from apps.students.models import EnrollmentStatus
from apps.institutions.models import AcademicLevel, AcademicSublevel


CATALOGS = {
    "document_types": {
        "model": DocumentType,
        "data": [
            {"code": "CC", "name": "Cédula de Ciudadanía"},
            {"code": "CE", "name": "Cédula de Extranjería"},
            {"code": "PP", "name": "Pasaporte"},
            {"code": "RC", "name": "Registro Civil"},
            {"code": "TI", "name": "Tarjeta de Identidad"},
            {"code": "NIT", "name": "NIT"},
        ],
    },
    "attendance_statuses": {
        "model": AttendanceStatus,
        "data": [
            {"code": "P", "name": "Presente"},
            {"code": "A", "name": "Ausente"},
            {"code": "T", "name": "Tardanza"},
            {"code": "J", "name": "Justificado"},
        ],
    },
    "grade_types": {
        "model": GradeType,
        "data": [
            {"code": "NUM", "name": "Numérica"},
            {"code": "CUAL", "name": "Cualitativa"},
            {"code": "RECUP", "name": "Recuperación"},
        ],
    },
    "qualitative_scales": {
        "model": QualitativeScale,
        "data": [
            {"code": "SE", "description": "Superior", "numeric_equivalence": 9.0, "name": "Superior"},
            {"code": "SA", "description": "Alto", "numeric_equivalence": 7.0, "name": "Alto"},
            {"code": "AC", "description": "Básico", "numeric_equivalence": 5.0, "name": "Básico"},
            {"code": "NA", "description": "No alcanzado", "numeric_equivalence": 3.0, "name": "No alcanzado"},
        ],
    },
    "period_types": {
        "model": PeriodType,
        "data": [
            {"code": "REGULAR", "name": "Regular"},
            {"code": "SUPLETORIO", "name": "Supletorio"},
            {"code": "REFUERZO", "name": "Refuerzo"},
        ],
    },
    "activity_types": {
        "model": ActivityType,
        "data": [
            {"code": "TAREA", "name": "Tarea"},
            {"code": "LECCION_ORAL", "name": "Lección Oral"},
            {"code": "TALLER", "name": "Taller"},
            {"code": "EXAMEN", "name": "Examen"},
            {"code": "PROYECTO", "name": "Proyecto"},
            {"code": "INVESTIGACION", "name": "Investigación"},
        ],
    },
    "evaluation_types": {
        "model": EvaluationType,
        "data": [
            {"code": "DIAGNOSTICA", "name": "Diagnóstica"},
            {"code": "FORMATIVA", "name": "Formativa"},
            {"code": "SUMATIVA", "name": "Sumativa"},
        ],
    },
    "promotion_statuses": {
        "model": PromotionStatus,
        "data": [
            {"code": "approved", "name": "Aprobado"},
            {"code": "failed", "name": "Reprobado"},
            {"code": "recovery", "name": "En Recuperación"},
        ],
    },
    "recovery_process_types": {
        "model": RecoveryProcessType,
        "data": [
            {"code": "MEJORA_DIRECTA", "name": "Mejora Directa"},
            {"code": "MEJORA_CON_REFUERZO", "name": "Mejora con Refuerzo"},
            {"code": "SUPLETORIA", "name": "Supletoria"},
        ],
    },
    "absence_types": {
        "model": AbsenceType,
        "data": [
            {"code": "justified", "name": "Justificada"},
            {"code": "unjustified", "name": "Injustificada"},
            {"code": "late", "name": "Atraso"},
            {"code": "none", "name": "Sin falta"},
        ],
    },
    "incident_types": {
        "model": IncidentType,
        "data": [
            {"code": "LEVE", "name": "Leve"},
            {"code": "MODERADO", "name": "Moderado"},
            {"code": "GRAVE", "name": "Grave"},
            {"code": "MUY_GRAVE", "name": "Muy Grave"},
        ],
    },
    "socioemotional_skills": {
        "model": SocioemotionalSkill,
        "data": [
            {"code": "EMPATIA", "name": "Empatía"},
            {"code": "AUTORREGULACION", "name": "Autorregulación"},
            {"code": "RESPONSABILIDAD", "name": "Responsabilidad"},
            {"code": "TRABAJO_EQUIPO", "name": "Trabajo en Equipo"},
            {"code": "COMUNICACION", "name": "Comunicación Asertiva"},
        ],
    },
    "subjects": {
        "model": Subject,
        "data": [
            {"code": "MAT", "name": "Matemáticas"},
            {"code": "LEN", "name": "Lengua y Literatura"},
            {"code": "CIE", "name": "Ciencias Naturales"},
            {"code": "SOC", "name": "Estudios Sociales"},
            {"code": "ING", "name": "Inglés"},
            {"code": "EDU_FIS", "name": "Educación Física"},
            {"code": "EDU_ART", "name": "Educación Artística"},
        ],
    },

    "alert_types": {
        "model": AlertType,
        "data": [
            {"code": "low_attendance", "name": "Baja Asistencia"},
            {"code": "failing_grades", "name": "Calificaciones Bajas"},
            {"code": "behavioral", "name": "Problemas de Conducta"},
            {"code": "dropout_risk", "name": "Riesgo de Deserción"},
            {"code": "socioemotional", "name": "Problemas Socioemocionales"},
        ],
    },
    "urgency_levels": {
        "model": UrgencyLevel,
        "data": [
            {"code": "low", "name": "Baja"},
            {"code": "medium", "name": "Media"},
            {"code": "high", "name": "Alta"},
            {"code": "critical", "name": "Crítica"},
        ],
    },
    "risk_factors": {
        "model": RiskFactor,
        "data": [
            {"code": "LOW_ATTENDANCE", "name": "Baja Asistencia"},
            {"code": "FAILING_GRADES", "name": "Calificaciones Bajas"},
            {"code": "BEHAVIOR_ISSUES", "name": "Problemas de Conducta"},
            {"code": "SOCIOEMOTIONAL", "name": "Problemas Socioemocionales"},
            {"code": "HIGH-absences", "name": "Ausentismo Frecuente"},
        ],
    },
    "sync_operations": {
        "model": SyncOperation,
        "data": [
            {"code": "INSERT", "name": "Insertar"},
            {"code": "UPDATE", "name": "Actualizar"},
            {"code": "DELETE", "name": "Eliminar"},
        ],
    },
    "sync_statuses": {
        "model": SyncStatus,
        "data": [
            {"code": "PENDIENTE", "name": "Pendiente"},
            {"code": "PROCESADO", "name": "Procesado"},
            {"code": "ERROR", "name": "Error"},
        ],
    },
    "academic_levels": {
        "model": AcademicLevel,
        "data": [
            {"code": "EGB", "name": "Educación General Básica"},
            {"code": "BGU", "name": "Bachillerato General Unificado"},
        ],
    },
    "enrollment_statuses": {
        "model": EnrollmentStatus,
        "data": [
            {"code": "ACT", "name": "Activa"},
            {"code": "RET", "name": "Retirado"},
            {"code": "TRS", "name": "Transferido"},
            {"code": "SUS", "name": "Suspendido"},
            {"code": "GRA", "name": "Graduado"},
        ],
    },
}


class Command(BaseCommand):
    help = "Seed catalog tables with initial data"

    def handle(self, *args, **options):
        created_count = 0
        existing_count = 0

        for catalog_name, catalog in CATALOGS.items():
            model = catalog["model"]
            entries = catalog["data"]
            for entry in entries:
                _, created = model.objects.get_or_create(
                    code=entry["code"], defaults=entry
                )
                if created:
                    created_count += 1
                else:
                    existing_count += 1

        # AcademicSublevel requiere FK academic_level (no se puede crear en el loop genérico)
        nivel_egb = AcademicLevel.objects.get(code="EGB")
        nivel_bgu = AcademicLevel.objects.get(code="BGU")
        sublevels = [
            {"code": "PREPARATORIA", "name": "Preparatoria", "academic_level": nivel_egb},
            {"code": "BASICA_ELEMENTAL", "name": "Básica Elemental", "academic_level": nivel_egb},
            {"code": "BASICA_MEDIA", "name": "Básica Media", "academic_level": nivel_egb},
            {"code": "BASICA_SUPERIOR", "name": "Básica Superior", "academic_level": nivel_egb},
            {"code": "BACHILLERATO", "name": "Bachillerato", "academic_level": nivel_bgu},
        ]
        for data in sublevels:
            _, created = AcademicSublevel.objects.get_or_create(
                code=data["code"], defaults=data
            )
            if created:
                created_count += 1
            else:
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Catalogs seed complete: {created_count} created, "
                f"{existing_count} already existed"
            )
        )
