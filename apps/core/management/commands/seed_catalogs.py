"""
seed_catalogs.py
Management command: seed_catalogs
Pobla las tablas de catálogo (valores estables que no cambian entre entornos).
Idempotente: get_or_create garantiza que re-ejecuciones no duplican registros.
"""
from django.core.management.base import BaseCommand

from apps.people.models import City, DocumentType
from apps.academic.period_type import PeriodType
from apps.academic.subject import Subject
from apps.grading.qualitative_scale import QualitativeScale
from apps.grading.activity_type import ActivityType
from apps.attendance.attendance_status import AttendanceStatus
from apps.attendance.absence_type import AbsenceType
from apps.behavior.incident_type import IncidentType
from apps.behavior.severity import Severity
from apps.analytics.student_risk import RiskFactor
from apps.students.models import WithdrawalReason, SpecialNeedsType, Kinship
from apps.institutions.academic_level import AcademicLevel
from apps.institutions.academic_sublevel import AcademicSublevel

# ---------------------------------------------------------------------------
# Datos de catálogo
# ---------------------------------------------------------------------------

CATALOGS = {
    # ------------------------------------------------------------------
    # Geografía
    # ------------------------------------------------------------------
    "cities": {
        "model": City,
        "data": [
            {"code": "ZARU",  "name": "Zaruma",     "is_active": True},
            {"code": "PINA",  "name": "Piñas",       "is_active": True},
            {"code": "PORTO", "name": "Portovelo",   "is_active": True},
            {"code": "MILAG", "name": "Milagro",     "is_active": True},
            {"code": "GUAYA", "name": "Guayaquil",   "is_active": True},
        ],
    },

    # ------------------------------------------------------------------
    # Tipos de documento de identidad (Ecuador)
    # ------------------------------------------------------------------
    "document_types": {
        "model": DocumentType,
        "data": [
            {"code": "CC",  "name": "Cédula de Ciudadanía",  "is_active": True},
            {"code": "CE",  "name": "Cédula de Extranjería", "is_active": True},
            {"code": "PP",  "name": "Pasaporte",             "is_active": True},
            {"code": "RC",  "name": "Registro Civil",        "is_active": True},
            {"code": "TI",  "name": "Tarjeta de Identidad",  "is_active": True},
        ],
    },

    # ------------------------------------------------------------------
    # Estados de asistencia
    # ------------------------------------------------------------------
    "attendance_statuses": {
        "model": AttendanceStatus,
        "data": [
            {
                "code": "P",
                "name": "Presente",
                "description": "Estudiante asistió a clase puntualmente",
                "is_active": True,
            },
            {
                "code": "A",
                "name": "Ausente",
                "description": "Estudiante no asistió a clase",
                "is_active": True,
            },
            {
                "code": "T",
                "name": "Tardanza",
                "description": "Estudiante llegó con retraso a clase",
                "is_active": True,
            },
            {
                "code": "J",
                "name": "Justificado",
                "description": "Ausencia justificada con documentación válida",
                "is_active": True,
            },
        ],
    },

    # ------------------------------------------------------------------
    # Escala cualitativa de calificaciones (BGU – Ecuador)
    # ------------------------------------------------------------------
    "qualitative_scales": {
        "model": QualitativeScale,
        "data": [
            {
                "code": "SE",
                "name": "Superior",
                "description": "Dominio excelente de los aprendizajes requeridos",
                "numeric_equivalence": 9.0,
                "is_active": True,
            },
            {
                "code": "SA",
                "name": "Alto",
                "description": "Dominio satisfactorio de los aprendizajes requeridos",
                "numeric_equivalence": 7.0,
                "is_active": True,
            },
            {
                "code": "AC",
                "name": "Básico",
                "description": "Dominio mínimo de los aprendizajes requeridos",
                "numeric_equivalence": 5.0,
                "is_active": True,
            },
            {
                "code": "NA",
                "name": "No alcanzado",
                "description": "No alcanza los aprendizajes mínimos requeridos",
                "numeric_equivalence": 3.0,
                "is_active": True,
            },
        ],
    },

    # ------------------------------------------------------------------
    # Tipos de período académico
    # ------------------------------------------------------------------
    "period_types": {
        "model": PeriodType,
        "data": [
            {
                "code": "TRIMESTRE",
                "name": "Trimestre",
                "description": "División del año escolar en 3 períodos de aproximadamente 3 meses",
                "divisions_per_year": 3,
                "is_active": True,
            },
            {
                "code": "QUIMESTRE",
                "name": "Quimestre",
                "description": "División del año escolar en 2 períodos de 5 meses",
                "divisions_per_year": 2,
                "is_active": True,
            },
            {
                "code": "BIMESTRE",
                "name": "Bimestre",
                "description": "División del año escolar en 4 períodos de 2 meses",
                "divisions_per_year": 4,
                "is_active": True,
            },
            {
                "code": "SEMESTRE",
                "name": "Semestre",
                "description": "División del año escolar en 2 períodos de 6 meses",
                "divisions_per_year": 2,
                "is_active": True,
            },
            {
                "code": "ANUAL",
                "name": "Anual",
                "description": "Período único que cubre todo el año escolar",
                "divisions_per_year": 1,
                "is_active": True,
            },
        ],
    },

    # ------------------------------------------------------------------
    # Tipos de actividad evaluativa
    # ------------------------------------------------------------------
    "activity_types": {
        "model": ActivityType,
        "data": [
            {
                "code": "TAREA",
                "name": "Tarea",
                "description": "Trabajo asignado para realizar fuera de clase",
                "is_active": True,
            },
            {
                "code": "LECCION_ORAL",
                "name": "Lección Oral",
                "description": "Evaluación oral individual o grupal frente al docente",
                "is_active": True,
            },
            {
                "code": "TALLER",
                "name": "Taller",
                "description": "Actividad práctica realizada en el aula",
                "is_active": True,
            },
            {
                "code": "EXAMEN",
                "name": "Examen",
                "description": "Evaluación escrita formal de conocimientos",
                "is_active": True,
            },
            {
                "code": "PROYECTO",
                "name": "Proyecto",
                "description": "Trabajo integrador de mediano o largo plazo",
                "is_active": True,
            },
            {
                "code": "INVESTIGACION",
                "name": "Investigación",
                "description": "Trabajo de investigación documental o de campo",
                "is_active": True,
            },
            {
                "code": "EXPOSICION",
                "name": "Exposición",
                "description": "Presentación oral de un tema ante el grupo",
                "is_active": True,
            },
        ],
    },

    # ------------------------------------------------------------------
    # Tipos de ausencia / falta
    # ------------------------------------------------------------------
    "absence_types": {
        "model": AbsenceType,
        "data": [
            {
                "code": "justified",
                "name": "Justificada",
                "description": "Ausencia con justificación válida (médica, familiar u oficial)",
                "is_active": True,
            },
            {
                "code": "unjustified",
                "name": "Injustificada",
                "description": "Ausencia sin justificación presentada",
                "is_active": True,
            },
            {
                "code": "late",
                "name": "Atraso",
                "description": "Llegada tardía registrada formalmente",
                "is_active": True,
            },
            {
                "code": "none",
                "name": "Sin falta",
                "description": "Registro sin ninguna falta asociada",
                "is_active": True,
            },
        ],
    },

    # ------------------------------------------------------------------
    # Tipos de incidente conductual
    # ------------------------------------------------------------------
    "incident_types": {
        "model": IncidentType,
        "data": [
            {
                "code": "PERTURBACION",
                "name": "Perturbación del orden",
                "description": "Comportamiento que interrumpe el desarrollo normal de la clase",
                "is_active": True,
            },
            {
                "code": "IRRESPETO",
                "name": "Irrespeto a compañero",
                "description": "Actitud irrespetuosa hacia un compañero dentro o fuera del aula",
                "is_active": True,
            },
            {
                "code": "IRRESPETO_DOC",
                "name": "Irrespeto a docente",
                "description": "Actitud irrespetuosa o desafiante hacia un docente o autoridad",
                "is_active": True,
            },
            {
                "code": "ACOSO",
                "name": "Acoso o bullying",
                "description": "Comportamiento sistemático de hostigamiento hacia un compañero",
                "is_active": True,
            },
            {
                "code": "DANO_PROPIEDAD",
                "name": "Daño a propiedad",
                "description": "Deterioro o destrucción de bienes del plantel o de compañeros",
                "is_active": True,
            },
            {
                "code": "INASISTENCIA",
                "name": "Inasistencia reiterada",
                "description": "Patrón de ausencias injustificadas frecuentes",
                "is_active": True,
            },
        ],
    },

    # ------------------------------------------------------------------
    # Asignaturas (catálogo global; la carga horaria se define por grado)
    # ------------------------------------------------------------------
    "subjects": {
        "model": Subject,
        "data": [
            {"code": "MAT",     "name": "Matemática",              "is_active": True},
            {"code": "LEN",     "name": "Lengua y Literatura",     "is_active": True},
            {"code": "FIS",     "name": "Física",                  "is_active": True},
            {"code": "QUI",     "name": "Química",                 "is_active": True},
            {"code": "BIO",     "name": "Biología",                "is_active": True},
            {"code": "SOC",     "name": "Historia y Ciencias Sociales", "is_active": True},
            {"code": "ING",     "name": "Inglés",                  "is_active": True},
            {"code": "FIL",     "name": "Filosofía",               "is_active": True},
            {"code": "EDU_FIS", "name": "Educación Física",        "is_active": True},
            {"code": "EDU_ART", "name": "Educación Cultural y Artística", "is_active": True},
            # Mantenidos por compatibilidad con grados previos
            {"code": "CIE",     "name": "Ciencias Naturales",      "is_active": True},
        ],
    },

    # ------------------------------------------------------------------
    # Factores de riesgo (analytics / modelo predictivo)
    # ------------------------------------------------------------------
    "risk_factors": {
        "model": RiskFactor,
        "data": [
            {
                "code": "LOW_ATTENDANCE",
                "name": "Baja Asistencia",
                "description": "Porcentaje de asistencia inferior al 80 %",
            },
            {
                "code": "FAILING_GRADES",
                "name": "Calificaciones Bajas",
                "description": "Promedio de calificaciones inferior a 7.00 sobre 10",
            },
            {
                "code": "BEHAVIOR_ISSUES",
                "name": "Problemas de Conducta",
                "description": "Múltiples incidentes conductuales registrados en el período",
            },
            {
                "code": "SOCIOEMOTIONAL",
                "name": "Indicadores Socioemocionales",
                "description": "Señales de dificultades emocionales, sociales o familiares",
            },
            {
                "code": "HIGH_ABSENCES",
                "name": "Ausentismo Frecuente",
                "description": "Más de 10 ausencias injustificadas en el período",
            },
            {
                "code": "GRADE_DECLINE",
                "name": "Descenso Sostenido de Notas",
                "description": "Tendencia negativa en el promedio de calificaciones entre períodos",
            },
        ],
    },

    # ------------------------------------------------------------------
    # Niveles académicos del sistema educativo ecuatoriano
    # ------------------------------------------------------------------
    "academic_levels": {
        "model": AcademicLevel,
        "data": [
            {"code": "EGB", "name": "Educación General Básica",       "is_active": True},
            {"code": "BGU", "name": "Bachillerato General Unificado", "is_active": True},
        ],
    },

    # ------------------------------------------------------------------
    # Razones de retiro / egreso anticipado
    # ------------------------------------------------------------------
    "withdrawal_reasons": {
        "model": WithdrawalReason,
        "data": [
            {
                "code": "CAMBIO_DOMICILIO",
                "name": "Cambio de domicilio",
                "description": "El estudiante o su familia se muda a otra zona o ciudad",
                "is_active": True,
            },
            {
                "code": "TRASLADO",
                "name": "Traslado a otra institución",
                "description": "El estudiante se transfiere a otra institución educativa",
                "is_active": True,
            },
            {
                "code": "FAMILIARES",
                "name": "Motivos familiares",
                "description": "Situaciones familiares que impiden la continuidad escolar",
                "is_active": True,
            },
            {
                "code": "SALUD",
                "name": "Razones de salud",
                "description": "Condición de salud que impide la asistencia regular",
                "is_active": True,
            },
            {
                "code": "TRABAJO",
                "name": "Ingreso al mercado laboral",
                "description": "El estudiante abandona el sistema escolar para trabajar",
                "is_active": True,
            },
            {
                "code": "DESISTIMIENTO",
                "name": "Desistimiento voluntario",
                "description": "El estudiante decide voluntariamente abandonar los estudios",
                "is_active": True,
            },
            {
                "code": "OTRO",
                "name": "Otro",
                "description": "Razón no contemplada en las categorías anteriores",
                "is_active": True,
            },
        ],
    },

    # ------------------------------------------------------------------
    # Tipos de necesidades educativas especiales (NEE)
    # ------------------------------------------------------------------
    "special_needs_types": {
        "model": SpecialNeedsType,
        "data": [
            {
                "code": "DISCAPACIDAD_FISICA",
                "name": "Discapacidad Física",
                "description": "Limitación motora que requiere adaptaciones físicas o de accesibilidad",
                "is_active": True,
            },
            {
                "code": "DISCAPACIDAD_SENSORIAL",
                "name": "Discapacidad Sensorial",
                "description": "Limitación visual o auditiva que requiere adaptaciones sensoriales",
                "is_active": True,
            },
            {
                "code": "DISCAPACIDAD_INTELECTUAL",
                "name": "Discapacidad Intelectual",
                "description": "Limitación cognitiva que requiere adaptaciones curriculares",
                "is_active": True,
            },
            {
                "code": "TRASTORNOS_APRENDIZAJE",
                "name": "Trastornos del Aprendizaje",
                "description": "Dislexia, disgrafía, discalculia u otros trastornos específicos del aprendizaje",
                "is_active": True,
            },
            {
                "code": "TDAH",
                "name": "TDAH",
                "description": "Trastorno por Déficit de Atención e Hiperactividad",
                "is_active": True,
            },
            {
                "code": "AUTISMO",
                "name": "Trastorno del Espectro Autista",
                "description": "TEA con distintos niveles de soporte requerido",
                "is_active": True,
            },
            {
                "code": "OTRO",
                "name": "Otra NEE",
                "description": "Necesidad educativa especial no especificada en el catálogo",
                "is_active": True,
            },
        ],
    },

    # ------------------------------------------------------------------
    # Parentescos / vínculos de representación
    # ------------------------------------------------------------------
    "kinships": {
        "model": Kinship,
        "data": [
            {
                "code": "PADRE",
                "name": "Padre",
                "description": "Padre biológico o adoptivo del estudiante",
                "is_active": True,
            },
            {
                "code": "MADRE",
                "name": "Madre",
                "description": "Madre biológica o adoptiva del estudiante",
                "is_active": True,
            },
            {
                "code": "ABUELO",
                "name": "Abuelo/a",
                "description": "Abuelo o abuela del estudiante con custodia o representación",
                "is_active": True,
            },
            {
                "code": "TIO",
                "name": "Tío/a",
                "description": "Tío o tía del estudiante",
                "is_active": True,
            },
            {
                "code": "HERMANO",
                "name": "Hermano/a mayor",
                "description": "Hermano o hermana mayor de edad con representación legal",
                "is_active": True,
            },
            {
                "code": "TUTOR",
                "name": "Tutor legal",
                "description": "Persona con tutela legal o representación judicial del estudiante",
                "is_active": True,
            },
            {
                "code": "OTRO",
                "name": "Otro vínculo",
                "description": "Otro tipo de parentesco o relación de representación",
                "is_active": True,
            },
        ],
    },

    # ------------------------------------------------------------------
    # Severidades de faltas conductuales
    # ------------------------------------------------------------------
    "severities": {
        "model": Severity,
        "data": [
            {
                "code": "LEVE",
                "name": "Falta leve",
                "description": "Falta que no interrumpe significativamente el proceso educativo",
                "is_active": True,
            },
            {
                "code": "MODERADA",
                "name": "Falta moderada",
                "description": "Falta que afecta el clima del aula y requiere intervención del docente",
                "is_active": True,
            },
            {
                "code": "GRAVE",
                "name": "Falta grave",
                "description": "Falta que requiere intervención de autoridades del plantel",
                "is_active": True,
            },
            {
                "code": "MUY_GRAVE",
                "name": "Falta muy grave",
                "description": "Falta que pone en riesgo la integridad de personas o bienes",
                "is_active": True,
            },
        ],
    },
}


class Command(BaseCommand):
    help = "Siembra las tablas de catálogo con datos iniciales (idempotente)"

    def handle(self, *args, **options):
        created_count = 0
        existing_count = 0

        for catalog_name, catalog in CATALOGS.items():
            model = catalog["model"]
            for entry in catalog["data"]:
                _, created = model.objects.get_or_create(
                    code=entry["code"], defaults=entry
                )
                if created:
                    created_count += 1
                else:
                    existing_count += 1

        # ----------------------------------------------------------------
        # AcademicSublevel: requiere FK a AcademicLevel
        # ----------------------------------------------------------------
        nivel_egb = AcademicLevel.objects.get(code="EGB")
        nivel_bgu = AcademicLevel.objects.get(code="BGU")

        sublevels = [
            {
                "code": "PREPARATORIA",
                "name": "Preparatoria",
                "description": "Nivel inicial del sistema educativo (1er grado)",
                "academic_level": nivel_egb,
                "is_active": True,
            },
            {
                "code": "BASICA_ELEMENTAL",
                "name": "Básica Elemental",
                "description": "Primer ciclo de EGB (2do a 4to grado)",
                "academic_level": nivel_egb,
                "is_active": True,
            },
            {
                "code": "BASICA_MEDIA",
                "name": "Básica Media",
                "description": "Segundo ciclo de EGB (5to a 7mo grado)",
                "academic_level": nivel_egb,
                "is_active": True,
            },
            {
                "code": "BASICA_SUPERIOR",
                "name": "Básica Superior",
                "description": "Tercer ciclo de EGB (8vo a 10mo grado)",
                "academic_level": nivel_egb,
                "is_active": True,
            },
            {
                "code": "BACHILLERATO",
                "name": "Bachillerato General Unificado",
                "description": "Educación media superior (1ro a 3ro BGU)",
                "academic_level": nivel_bgu,
                "is_active": True,
            },
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
                f"Catálogos: {created_count} registros creados, "
                f"{existing_count} ya existían."
            )
        )
