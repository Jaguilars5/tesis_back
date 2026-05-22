from django.core.management.base import BaseCommand

from apps.analytics.models import RiskFactor
from apps.grading.models import AttendanceStatus, GradeType, QualitativeScale
from apps.institutions.models import DocumentType, RoomType
from apps.students.models import EnrollmentStatus


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
    "room_types": {
        "model": RoomType,
        "data": [
            {"code": "AULA", "name": "Aula de Clase"},
            {"code": "LAB", "name": "Laboratorio"},
            {"code": "AUDIT", "name": "Auditorio"},
            {"code": "CANCH", "name": "Cancha"},
            {"code": "SALA_PROF", "name": "Sala de Profesores"},
            {"code": "BIB", "name": "Biblioteca"},
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
            {"code": "SE", "description": "Superior", "numeric_equivalence": 9.0},
            {"code": "SA", "description": "Alto", "numeric_equivalence": 7.0},
            {"code": "AC", "description": "Básico", "numeric_equivalence": 5.0},
            {"code": "NA", "description": "No alcanzado", "numeric_equivalence": 3.0},
        ],
    },
    "enrollment_statuses": {
        "model": EnrollmentStatus,
        "data": [
            {"code": "ACT", "name": "Activa"},
            {"code": "RET", "name": "Retirado"},
            {"code": "GRAD", "name": "Graduado"},
            {"code": "TRAS", "name": "Transferido"},
            {"code": "SUSP", "name": "Suspendido"},
        ],
    },
    "risk_factors": {
        "model": RiskFactor,
        "data": [
            {
                "code": "ASIST_BAJA",
                "name": "Asistencia Baja",
                "description": "Estudiante con alta tasa de inasistencia",
            },
            {
                "code": "REND_DECL",
                "name": "Rendimiento Declinante",
                "description": "Estudiante con tendencia descendente en calificaciones",
            },
            {
                "code": "COND_NEG",
                "name": "Conducta Negativa",
                "description": "Estudiante con incidentes de conducta frecuentes",
            },
            {
                "code": "BAJO_REND",
                "name": "Bajo Rendimiento",
                "description": "Estudiante con calificaciones por debajo del promedio",
            },
            {
                "code": "FAM_NO_NOTIF",
                "name": "Familia No Notificada",
                "description": "Estudiante cuyos representantes no han sido contactados",
            },
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

        self.stdout.write(
            self.style.SUCCESS(
                f"Catalogs seed complete: {created_count} created, "
                f"{existing_count} already existed"
            )
        )
