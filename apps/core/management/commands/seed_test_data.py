"""
seed_test_data.py
Management command: seed_test_data
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pobla la base de datos con datos realistas para el año lectivo 2025-2026.
Nivel creado: Primero de Bachillerato (1ro BGU), paralelos A y B.

Características:
  • Año lectivo 2025-2026 (cierre administrativo hasta 31-jul-2026) en 3 trimestres
  • Clases, asistencia y entregas solo hasta el 30-jun-2026
  • 7 asignaturas del currículo BGU, un docente titular por asignatura
  • 12 estudiantes por paralelo (24 en total)
  • Cada estudiante tiene exactamente un representante primario
  • Algunos representantes están vinculados a dos hermanos (max 2 estudiantes)
  • Horario sin cruces ni solapamientos entre docentes, materias y paralelos
  • Actividades evaluativas con nombres descriptivos por asignatura y trimestre
  • Notas con distribución variada entre 0 y 10 (no todas iguales)
  • Incidentes conductuales con descripciones realistas por tipo
  • Idempotente: re-ejecutar no duplica registros

Credenciales generadas por convención (el acceso en el sistema es por username):
  Docentes       → usuario: <inicial_nombre><apellido> (ej. cvillacis) / pw: Doc.<Apellido>2025!
  Estudiantes    → usuario: <inicial_nombre><apellido> / pw: Est.<Apellido>2025!
  Representantes → usuario: <inicial_nombre><apellido> / pw: Rep.<Apellido>2025!
  Admin/Director → usuario: <inicial_nombre><apellido> (ej. sadministrador) / pw: Admin@uetest2025!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import datetime
import random
from datetime import date
from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.academic.academic_period import AcademicPeriod
from apps.academic.class_schedule import ClassSchedule
from apps.academic.period_type import PeriodType
from apps.academic.subject import Subject
from apps.academic.subject_academic_config import SubjectAcademicConfig
from apps.academic.subject_offering import SubjectOffering
from apps.academic.teacher_subject_section import TeacherSubjectSection
from apps.analytics.early_alert.infrastructure.models import EarlyAlert
from apps.analytics.student_risk import StudentFeatureSnapshot, StudentRiskScore
from apps.attendance.attendance_status import AttendanceStatus
from apps.attendance.attendance_core import Attendance
from apps.behavior.conduct_incident import ConductIncident
from apps.behavior.incident_type import IncidentType
from apps.behavior.severity import Severity
from apps.behavior.behavior_evaluation import BehaviorEvaluationService
from apps.grading.activity_type import ActivityType
from apps.grading.evaluation import EvaluationBlock, BlockComponent, EvaluativeActivity
from apps.grading.qualitative_scale import QualitativeScale
from apps.grading.student_note import StudentNote, GradeCalculationService
from apps.grading.student_note.signals import skip_period_summary_recalc
from apps.iam import Role, User, UserRole
from apps.institutions.school_year import SchoolYear
from apps.institutions.academic_level import AcademicLevel
from apps.institutions.academic_sublevel import AcademicSublevel
from apps.institutions.academic_grade import AcademicGrade
from apps.institutions.section import Section
from apps.people.models import DocumentType, Person
from apps.students.models import (
    Enrollment,
    Kinship,
    Student,
    StudentRepresentative,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Semilla aleatoria fija: resultados reproducibles entre ejecuciones
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RANDOM_SEED = 2025
random.seed(RANDOM_SEED)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATOS MAESTROS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SCHOOL_YEAR = {
    "name": "2025-2026",
    "start_date": date(2025, 9, 1),
    "end_date":   date(2026, 7, 31),
    "is_active":  True,
}

# Último día con clases / asistencia / entregas (julio = cierre administrativo del año)
ACTIVE_YEAR_INSTRUCTIONAL_END = date(2026, 6, 30)


def _instructional_end_date(period) -> date:
    """Fin de actividad lectiva del período (asistencia, tareas, incidentes en aula)."""
    if period.code.endswith("-2526"):
        return min(period.end_date, ACTIVE_YEAR_INSTRUCTIONAL_END)
    return period.end_date


# Tres trimestres del año lectivo 2025-2026 (cierre administrativo hasta fin de julio)
TRIMESTRES = [
    {
        "code":       "T1-2526",
        "name":       "Primer Trimestre",
        "start_date": date(2025, 9, 1),
        "end_date":   date(2025, 11, 30),
        "weight":     Decimal("33.33"),
    },
    {
        "code":       "T2-2526",
        "name":       "Segundo Trimestre",
        "start_date": date(2025, 12, 1),
        "end_date":   date(2026, 3, 20),
        "weight":     Decimal("33.33"),
    },
    {
        "code":       "T3-2526",
        "name":       "Tercer Trimestre",
        "start_date": date(2026, 3, 23),
        "end_date":   date(2026, 7, 31),
        "weight":     Decimal("33.34"),
    },
]

# ── Asignaturas 1ro BGU con carga horaria semanal ───────────────────────────
# (código, nombre visible, horas/semana)
MATERIAS_BGU = [
    ("MAT",     "Matemática",                       4),
    ("FIS",     "Física",                           4),
    ("QUI",     "Química",                          3),
    ("BIO",     "Biología",                         3),
    ("LEN",     "Lengua y Literatura",              4),
    ("ING",     "Inglés",                           5),
    ("SOC",     "Historia y Ciencias Sociales",     3),
    ("FIL",     "Filosofía",                        2),
    ("EDU_FIS", "Educación Física",                 2),
    ("EDU_ART", "Educación Cultural y Artística",   2),
]

# ── Docentes (un titular por asignatura) ─────────────────────────────────────
# Cada entrada: tag, cédula, nombres, apellidos, materia que dicta
DOCENTES = [
    {
        "tag":             "doc_mat",
        "document_number": "0901100001",
        "names":           "Carlos Ernesto",
        "last_names":      "Villacís Mora",
        "subject_code":    "MAT",
        "birth_date":      date(1978, 3, 15),
    },
    {
        "tag":             "doc_fis",
        "document_number": "0901100002",
        "names":           "Jorge Andrés",
        "last_names":      "Palacio Herrera",
        "subject_code":    "FIS",
        "birth_date":      date(1980, 7, 22),
    },
    {
        "tag":             "doc_qui",
        "document_number": "0901100003",
        "names":           "Patricia Elena",
        "last_names":      "Astudillo Guzmán",
        "subject_code":    "QUI",
        "birth_date":      date(1982, 11, 5),
    },
    {
        "tag":             "doc_bio",
        "document_number": "0901100004",
        "names":           "Margarita Isabel",
        "last_names":      "Rosero Caicedo",
        "subject_code":    "BIO",
        "birth_date":      date(1979, 4, 18),
    },
    {
        "tag":             "doc_len",
        "document_number": "0901100005",
        "names":           "Rodrigo Sebastián",
        "last_names":      "Cevallos Naranjo",
        "subject_code":    "LEN",
        "birth_date":      date(1975, 9, 30),
    },
    {
        "tag":             "doc_ing",
        "document_number": "0901100006",
        "names":           "Sandra Viviana",
        "last_names":      "Montenegro Vega",
        "subject_code":    "ING",
        "birth_date":      date(1985, 6, 12),
    },
    {
        "tag":             "doc_soc",
        "document_number": "0901100007",
        "names":           "Fernando Luis",
        "last_names":      "Aguilar Saltos",
        "subject_code":    "SOC",
        "birth_date":      date(1977, 1, 25),
    },
    {
        "tag":             "doc_fil",
        "document_number": "0901100008",
        "names":           "Ana Lucía",
        "last_names":      "Bravo Suárez",
        "subject_code":    "FIL",
        "birth_date":      date(1983, 8, 8),
    },
    {
        "tag":             "doc_edf",
        "document_number": "0901100009",
        "names":           "Miguel Ángel",
        "last_names":      "Freire Castillo",
        "subject_code":    "EDU_FIS",
        "birth_date":      date(1986, 2, 14),
    },
    {
        "tag":             "doc_art",
        "document_number": "0901100010",
        "names":           "Daniela Cristina",
        "last_names":      "Loor Peñaherrera",
        "subject_code":    "EDU_ART",
        "birth_date":      date(1990, 5, 20),
    },
]

# ── Usuarios administrativos ─────────────────────────────────────────────────
ADMIN_USERS = [
    {
        "tag":             "admin",
        "document_number": "0900000001",
        "names":           "Sistema",
        "last_names":      "Administrador",
        "email":           "admin@uetest.edu.ec",
        "password":        "Admin@uetest2025!",
        "is_superuser":    True,
        "role_code":       None,
        "birth_date":      date(1980, 1, 1),
    },
    {
        "tag":             "director",
        "document_number": "0900000002",
        "names":           "Ramiro Patricio",
        "last_names":      "Montoya Espinoza",
        "email":           "director@uetest.edu.ec",
        "password":        "Director@uetest2025!",
        "is_superuser":    False,
        "role_code":       "DIRECTOR",
        "birth_date":      date(1970, 6, 10),
    },
    {
        "tag":             "consejero",
        "document_number": "0900000003",
        "names":           "Lorena Beatriz",
        "last_names":      "Zamora Hidalgo",
        "email":           "consejero.dece@uetest.edu.ec",
        "password":        "Dece@uetest2025!",
        "is_superuser":    False,
        "role_code":       "CONSEJERO",
        "birth_date":      date(1984, 3, 22),
    },
]

# ── Estudiantes ───────────────────────────────────────────────────────────────
# 12 por paralelo A, 12 por paralelo B (24 total)
# Formato: tag, cédula, nombres, apellidos, paralelo, birth_date
ESTUDIANTES = [
    # ── Paralelo A ──────────────────────────────────────────────────────────
    {"tag": "est_a01", "document_number": "0910200101", "names": "Sebastián Andrés",   "last_names": "Almeida Ríos",       "parallel": "A", "birth_date": date(2009, 3, 12)},
    {"tag": "est_a02", "document_number": "0910200102", "names": "Camila Valentina",   "last_names": "Burbano Chávez",     "parallel": "A", "birth_date": date(2010, 7, 25)},
    {"tag": "est_a03", "document_number": "0910200103", "names": "Diego Alejandro",    "last_names": "Córdova Salinas",    "parallel": "A", "birth_date": date(2011, 1, 8)},
    {"tag": "est_a04", "document_number": "0910200104", "names": "Gabriela Mishell",   "last_names": "Delgado Vera",       "parallel": "A", "birth_date": date(2009, 11, 3)},
    {"tag": "est_a05", "document_number": "0910200105", "names": "Mateo Nicolás",      "last_names": "Espinoza Toro",      "parallel": "A", "birth_date": date(2010, 5, 17)},
    {"tag": "est_a06", "document_number": "0910200106", "names": "Andrea Sofía",       "last_names": "Flores Guamán",      "parallel": "A", "birth_date": date(2011, 2, 28)},
    {"tag": "est_a07", "document_number": "0910200107", "names": "Andrés Mauricio",    "last_names": "García Molina",      "parallel": "A", "birth_date": date(2009, 9, 14)},
    {"tag": "est_a08", "document_number": "0910200108", "names": "Valeria Nicole",     "last_names": "Herrera Pacheco",    "parallel": "A", "birth_date": date(2010, 4, 6)},
    {"tag": "est_a09", "document_number": "0910200109", "names": "Juan Pablo",         "last_names": "Intriago Barros",    "parallel": "A", "birth_date": date(2011, 8, 19)},
    {"tag": "est_a10", "document_number": "0910200110", "names": "Paola Estefanía",    "last_names": "Jiménez Olmedo",     "parallel": "A", "birth_date": date(2009, 12, 1)},
    {"tag": "est_a11", "document_number": "0910200111", "names": "Kevin Steeven",      "last_names": "Lara Morocho",       "parallel": "A", "birth_date": date(2010, 6, 22)},
    {"tag": "est_a12", "document_number": "0910200112", "names": "María Fernanda",     "last_names": "Morales Quiñónez",   "parallel": "A", "birth_date": date(2011, 3, 30)},

    # ── Paralelo B ──────────────────────────────────────────────────────────
    {"tag": "est_b01", "document_number": "0910200201", "names": "Luis Fernando",      "last_names": "Naranjo Ponce",      "parallel": "B", "birth_date": date(2009, 2, 11)},
    {"tag": "est_b02", "document_number": "0910200202", "names": "Priscila Marisol",   "last_names": "Ortega Sánchez",     "parallel": "B", "birth_date": date(2010, 10, 5)},
    {"tag": "est_b03", "document_number": "0910200203", "names": "Emilio Javier",      "last_names": "Peña Villamar",      "parallel": "B", "birth_date": date(2011, 4, 23)},
    {"tag": "est_b04", "document_number": "0910200204", "names": "Natalia Daniela",    "last_names": "Quito Benítez",      "parallel": "B", "birth_date": date(2009, 8, 9)},
    {"tag": "est_b05", "document_number": "0910200205", "names": "Pablo Rodrigo",      "last_names": "Romero Cárdenas",    "parallel": "B", "birth_date": date(2010, 1, 27)},
    {"tag": "est_b06", "document_number": "0910200206", "names": "Karla Alejandra",    "last_names": "Samaniego Torres",   "parallel": "B", "birth_date": date(2011, 6, 15)},
    {"tag": "est_b07", "document_number": "0910200207", "names": "Bryan Stalyn",       "last_names": "Tapia Guevara",      "parallel": "B", "birth_date": date(2009, 5, 4)},
    {"tag": "est_b08", "document_number": "0910200208", "names": "Alejandra Pamela",   "last_names": "Urgiles Montoya",    "parallel": "B", "birth_date": date(2010, 7, 18)},
    {"tag": "est_b09", "document_number": "0910200209", "names": "Cristian José",      "last_names": "Vargas Coello",      "parallel": "B", "birth_date": date(2011, 9, 7)},
    {"tag": "est_b10", "document_number": "0910200210", "names": "Melanie Yoselin",    "last_names": "Washburn Cajas",     "parallel": "B", "birth_date": date(2009, 5, 31)},
    {"tag": "est_b11", "document_number": "0910200211", "names": "Ronaldo Jesús",      "last_names": "Yánez Bustamante",   "parallel": "B", "birth_date": date(2010, 11, 16)},
    {"tag": "est_b12", "document_number": "0910200212", "names": "Carolina Liseth",    "last_names": "Zambrano Aguilar",   "parallel": "B", "birth_date": date(2011, 1, 20)},
]

# ── Representantes ─────────────────────────────────────────────────────────
# Reglas:
#   - Cada estudiante tiene EXACTAMENTE un representante primario
#   - Un representante puede tener 1 o 2 estudiantes (hermanos, nunca más de 2)
#   - Ningún representante queda sin estudiante asociado
#   - Parentesco y nombre coherentes con los estudiantes
#
# La columna "students" lista los tags de estudiantes que representa.
REPRESENTANTES = [
    # — Representantes de paralelo A ————————————————————————————————————————
    {
        "tag":             "rep_a01",
        "document_number": "0900100101",
        "names":           "Roberto Carlos",
        "last_names":      "Almeida Fuentes",
        "birth_date":      date(1980, 6, 5),
        "kinship_code":    "PADRE",
        "students":        ["est_a01"],          # Sebastián Almeida
    },
    {
        "tag":             "rep_a02",
        "document_number": "0900100102",
        "names":           "Lucía Adriana",
        "last_names":      "Burbano Estrella",
        "birth_date":      date(1982, 9, 14),
        "kinship_code":    "MADRE",
        "students":        ["est_a02"],          # Camila Burbano
    },
    {
        "tag":             "rep_a03",
        "document_number": "0900100103",
        "names":           "Hernán Eduardo",
        "last_names":      "Córdova Villacís",
        "birth_date":      date(1978, 12, 20),
        "kinship_code":    "PADRE",
        "students":        ["est_a03"],          # Diego Córdova
    },
    {
        "tag":             "rep_a04",
        "document_number": "0900100104",
        "names":           "Rosa Amparito",
        "last_names":      "Delgado Muñoz",
        "birth_date":      date(1983, 4, 11),
        "kinship_code":    "MADRE",
        "students":        ["est_a04"],          # Gabriela Delgado
    },
    {
        "tag":             "rep_a05",
        "document_number": "0900100105",
        "names":           "Nelson Patricio",
        "last_names":      "Espinoza Granda",
        "birth_date":      date(1975, 8, 30),
        "kinship_code":    "PADRE",
        "students":        ["est_a05"],          # Mateo Espinoza
    },
    {
        "tag":             "rep_a06",
        "document_number": "0900100106",
        "names":           "Silvia Marisol",
        "last_names":      "Flores Cedeño",
        "birth_date":      date(1985, 2, 7),
        "kinship_code":    "MADRE",
        "students":        ["est_a06"],          # Andrea Flores
    },
    {
        "tag":             "rep_a07",
        "document_number": "0900100107",
        "names":           "Marco Antonio",
        "last_names":      "García Mendoza",
        "birth_date":      date(1979, 11, 3),
        "kinship_code":    "PADRE",
        "students":        ["est_a07"],          # Andrés García
    },
    # rep_a08 representa dos hermanos: Valeria (A) y Bryan (B)
    {
        "tag":             "rep_a08",
        "document_number": "0900100108",
        "names":           "Isabel Rocío",
        "last_names":      "Herrera Salazar",
        "birth_date":      date(1981, 5, 25),
        "kinship_code":    "MADRE",
        "students":        ["est_a08", "est_b07"],   # Valeria Herrera + Bryan Tapia (nombre materno diferente, común en Ecuador)
    },
    {
        "tag":             "rep_a09",
        "document_number": "0900100109",
        "names":           "Oswaldo Ramiro",
        "last_names":      "Intriago Mero",
        "birth_date":      date(1977, 7, 19),
        "kinship_code":    "PADRE",
        "students":        ["est_a09"],          # Juan Pablo Intriago
    },
    {
        "tag":             "rep_a10",
        "document_number": "0900100110",
        "names":           "Carmen Auxiliadora",
        "last_names":      "Jiménez Palacios",
        "birth_date":      date(1980, 3, 8),
        "kinship_code":    "MADRE",
        "students":        ["est_a10"],          # Paola Jiménez
    },
    # rep_a11 representa dos hermanos: Kevin (A) y Luis (B)
    {
        "tag":             "rep_a11",
        "document_number": "0900100111",
        "names":           "Freddy Bolívar",
        "last_names":      "Lara Quinatoa",
        "birth_date":      date(1976, 10, 15),
        "kinship_code":    "PADRE",
        "students":        ["est_a11", "est_b01"],   # Kevin Lara + Luis Naranjo (madre diferente)
    },
    {
        "tag":             "rep_a12",
        "document_number": "0900100112",
        "names":           "Gloria Esperanza",
        "last_names":      "Morales Idrovo",
        "birth_date":      date(1982, 1, 28),
        "kinship_code":    "MADRE",
        "students":        ["est_a12"],          # María Fernanda Morales
    },

    # — Representantes de paralelo B ————————————————————————————————————————
    # (est_b01 y est_b07 ya están cubiertos por rep_a11 y rep_a08)
    {
        "tag":             "rep_b02",
        "document_number": "0900100202",
        "names":           "Leonidas Raúl",
        "last_names":      "Ortega Lozano",
        "birth_date":      date(1978, 4, 2),
        "kinship_code":    "PADRE",
        "students":        ["est_b02"],          # Priscila Ortega
    },
    {
        "tag":             "rep_b03",
        "document_number": "0900100203",
        "names":           "Verónica Susana",
        "last_names":      "Peña Sánchez",
        "birth_date":      date(1983, 6, 17),
        "kinship_code":    "MADRE",
        "students":        ["est_b03"],          # Emilio Peña
    },
    # rep_b04 representa dos hermanas: Natalia (B) y Carolina (B)
    {
        "tag":             "rep_b04",
        "document_number": "0900100204",
        "names":           "Blanca Noemí",
        "last_names":      "Quito Freire",
        "birth_date":      date(1980, 9, 23),
        "kinship_code":    "MADRE",
        "students":        ["est_b04", "est_b12"],  # Natalia Quito + Carolina Zambrano (padre diferente)
    },
    {
        "tag":             "rep_b05",
        "document_number": "0900100205",
        "names":           "Gonzalo Efraín",
        "last_names":      "Romero Iñiguez",
        "birth_date":      date(1975, 12, 10),
        "kinship_code":    "PADRE",
        "students":        ["est_b05"],          # Pablo Romero
    },
    {
        "tag":             "rep_b06",
        "document_number": "0900100206",
        "names":           "Alexandra Paola",
        "last_names":      "Samaniego Vilema",
        "birth_date":      date(1984, 7, 4),
        "kinship_code":    "MADRE",
        "students":        ["est_b06"],          # Karla Samaniego
    },
    {
        "tag":             "rep_b08",
        "document_number": "0900100208",
        "names":           "Rodrigo Marcelo",
        "last_names":      "Urgiles Merchán",
        "birth_date":      date(1977, 2, 14),
        "kinship_code":    "PADRE",
        "students":        ["est_b08"],          # Alejandra Urgiles
    },
    {
        "tag":             "rep_b09",
        "document_number": "0900100209",
        "names":           "Mariana Elizabeth",
        "last_names":      "Vargas Celi",
        "birth_date":      date(1981, 8, 29),
        "kinship_code":    "MADRE",
        "students":        ["est_b09"],          # Cristian Vargas
    },
    {
        "tag":             "rep_b10",
        "document_number": "0900100210",
        "names":           "Jonathan Xavier",
        "last_names":      "Washburn Vera",
        "birth_date":      date(1979, 5, 6),
        "kinship_code":    "PADRE",
        "students":        ["est_b10"],          # Melanie Washburn
    },
    {
        "tag":             "rep_b11",
        "document_number": "0900100211",
        "names":           "Piedad Aurora",
        "last_names":      "Yánez Álvarez",
        "birth_date":      date(1976, 11, 12),
        "kinship_code":    "MADRE",
        "students":        ["est_b11"],          # Ronaldo Yánez
    },
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HORARIO SIN CRUCES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Estructura del día: bloques de 45 min, 7:00-13:15, con recreo 10:00-10:15
#
#  Bloque 1  07:00 – 07:45
#  Bloque 2  07:45 – 08:30
#  Bloque 3  08:30 – 09:15
#  Bloque 4  09:15 – 10:00
#  [recreo]  10:00 – 10:15
#  Bloque 5  10:15 – 11:00
#  Bloque 6  11:00 – 11:45
#  Bloque 7  11:45 – 12:30
#  Bloque 8  12:30 – 13:15
#
# Reglas de cruce CERO:
#   1. El constraint del modelo es (teacher_subject_section, day_of_week, start_time).
#      El mismo TSS no puede tener dos entradas con mismo día + hora inicio.
#   2. Un docente puede dictar al mismo día a A y a B SOLO si sus bloques
#      no se solapan en tiempo (bloques 1-4 para uno, bloques 5-8 para el otro).
#   3. Un paralelo no puede tener dos materias en el mismo bloque horario.
#
# Diseño aplicado:
#   Lunes    → A en bloques 1-4  (MAT×2, LEN, ING)        B en bloques 5-8  (FIS×2, SOC, ING)
#   Martes   → A en bloques 1-4  (FIS×2, QUI, SOC)        B en bloques 5-8  (MAT×2, LEN, QUI)
#   Miércoles→ A en bloques 1-4  (ING, BIO, FIL, EDU_ART) B en bloques 5-8  (ING, BIO, FIL, EDU_ART)
#   Jueves   → A en bloques 1-4  (LEN, MAT, ING, EDU_FIS) B en bloques 5-8  (LEN, MAT, ING, EDU_FIS)
#   Viernes  → A en bloques 1-4  (QUI, SOC, LEN, BIO)     B en bloques 5-8  (QUI, SOC, LEN, BIO)
#
# Horas semanales resultantes (cada slot = 45 min ≈ 1 hora pedagógica):
#   MAT 4 | FIS 4 | QUI 3 | BIO 3 | LEN 4 | ING 5 | SOC 3 | FIL 2 | EDU_FIS 2 | EDU_ART 2
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _t(h: int, m: int) -> datetime.time:
    """Atajo para construir un datetime.time."""
    return datetime.time(h, m)


# Formato: (subject_code, parallel, day_of_week, start_time, end_time)

SCHEDULE_SLOTS = [
    # ── LUNES ────────────────────────────────────────────────────────────────
    # Paralelo A (bloques 1-4): MAT MAT LEN ING
    ("MAT", "A", 1, _t(7,  0), _t(7, 45)),
    ("MAT", "A", 1, _t(7, 45), _t(8, 30)),
    ("LEN", "A", 1, _t(8, 30), _t(9, 15)),
    ("ING", "A", 1, _t(9, 15), _t(10, 0)),
    # Paralelo B (bloques 5-8): FIS FIS SOC ING
    # ING mismo día → A termina 10:00 / B empieza 12:30 → sin solapamiento ✓
    ("FIS", "B", 1, _t(10, 15), _t(11, 0)),
    ("FIS", "B", 1, _t(11,  0), _t(11, 45)),
    ("SOC", "B", 1, _t(11, 45), _t(12, 30)),
    ("ING", "B", 1, _t(12, 30), _t(13, 15)),

    # ── MARTES ───────────────────────────────────────────────────────────────
    # Paralelo A (bloques 1-4): FIS FIS QUI SOC
    ("FIS", "A", 2, _t(7,  0), _t(7, 45)),
    ("FIS", "A", 2, _t(7, 45), _t(8, 30)),
    ("QUI", "A", 2, _t(8, 30), _t(9, 15)),
    ("SOC", "A", 2, _t(9, 15), _t(10, 0)),
    # Paralelo B (bloques 5-8): MAT MAT LEN QUI
    # QUI mismo día → A termina 09:15 / B empieza 12:30 → sin solapamiento ✓
    ("MAT", "B", 2, _t(10, 15), _t(11, 0)),
    ("MAT", "B", 2, _t(11,  0), _t(11, 45)),
    ("LEN", "B", 2, _t(11, 45), _t(12, 30)),
    ("QUI", "B", 2, _t(12, 30), _t(13, 15)),

    # ── MIÉRCOLES ────────────────────────────────────────────────────────────
    # Cada docente atiende A en bloques 1-4 y B en bloques 5-8 del mismo día
    # Paralelo A: ING BIO FIL EDU_ART
    ("ING",     "A", 3, _t(7,  0), _t(7, 45)),
    ("BIO",     "A", 3, _t(7, 45), _t(8, 30)),
    ("FIL",     "A", 3, _t(8, 30), _t(9, 15)),
    ("EDU_ART", "A", 3, _t(9, 15), _t(10, 0)),
    # Paralelo B: ING BIO FIL EDU_ART
    # ING:     A 07:00-07:45 / B 10:15-11:00  → sin solapamiento ✓
    # BIO:     A 07:45-08:30 / B 11:00-11:45  → sin solapamiento ✓
    # FIL:     A 08:30-09:15 / B 11:45-12:30  → sin solapamiento ✓
    # EDU_ART: A 09:15-10:00 / B 12:30-13:15  → sin solapamiento ✓
    ("ING",     "B", 3, _t(10, 15), _t(11, 0)),
    ("BIO",     "B", 3, _t(11,  0), _t(11, 45)),
    ("FIL",     "B", 3, _t(11, 45), _t(12, 30)),
    ("EDU_ART", "B", 3, _t(12, 30), _t(13, 15)),

    # ── JUEVES ───────────────────────────────────────────────────────────────
    # Paralelo A: LEN MAT ING EDU_FIS
    ("LEN",     "A", 4, _t(7,  0), _t(7, 45)),
    ("MAT",     "A", 4, _t(7, 45), _t(8, 30)),
    ("ING",     "A", 4, _t(8, 30), _t(9, 15)),
    ("EDU_FIS", "A", 4, _t(9, 15), _t(10, 0)),
    # Paralelo B: LEN MAT ING EDU_FIS
    # LEN:     A 07:00-07:45 / B 10:15-11:00  → sin solapamiento ✓
    # MAT:     A 07:45-08:30 / B 11:00-11:45  → sin solapamiento ✓
    # ING:     A 08:30-09:15 / B 11:45-12:30  → sin solapamiento ✓
    # EDU_FIS: A 09:15-10:00 / B 12:30-13:15  → sin solapamiento ✓
    ("LEN",     "B", 4, _t(10, 15), _t(11, 0)),
    ("MAT",     "B", 4, _t(11,  0), _t(11, 45)),
    ("ING",     "B", 4, _t(11, 45), _t(12, 30)),
    ("EDU_FIS", "B", 4, _t(12, 30), _t(13, 15)),

    # ── VIERNES ──────────────────────────────────────────────────────────────
    # Paralelo A: QUI SOC LEN BIO
    ("QUI", "A", 5, _t(7,  0), _t(7, 45)),
    ("SOC", "A", 5, _t(7, 45), _t(8, 30)),
    ("LEN", "A", 5, _t(8, 30), _t(9, 15)),
    ("BIO", "A", 5, _t(9, 15), _t(10, 0)),
    # Paralelo B: QUI SOC LEN BIO
    # QUI: A 07:00-07:45 / B 10:15-11:00  → sin solapamiento ✓
    # SOC: A 07:45-08:30 / B 11:00-11:45  → sin solapamiento ✓
    # LEN: A 08:30-09:15 / B 11:45-12:30  → sin solapamiento ✓
    # BIO: A 09:15-10:00 / B 12:30-13:15  → sin solapamiento ✓
    ("QUI", "B", 5, _t(10, 15), _t(11, 0)),
    ("SOC", "B", 5, _t(11,  0), _t(11, 45)),
    ("LEN", "B", 5, _t(11, 45), _t(12, 30)),
    ("BIO", "B", 5, _t(12, 30), _t(13, 15)),
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ACTIVIDADES EVALUATIVAS POR ASIGNATURA Y TRIMESTRE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Formato por trimestre: (subject_code, component_name, activity_title, activity_type_code)
# component_name: "Tareas", "Lecciones", "Talleres"

ACTIVIDADES_POR_TRIMESTRE = {
    "T1-2526": [
        # Matemática
        ("MAT", "Tareas",    "Tarea 1: Funciones lineales y cuadráticas",              "TAREA"),
        ("MAT", "Tareas",    "Tarea 2: Sistemas de ecuaciones",                        "TAREA"),
        ("MAT", "Lecciones", "Lección oral: Números reales e irracionales",            "LECCION_ORAL"),
        ("MAT", "Talleres",  "Taller: Resolución de inecuaciones",                     "TALLER"),
        # Física
        ("FIS", "Tareas",    "Tarea 1: Cinemática – movimiento rectilíneo",            "TAREA"),
        ("FIS", "Lecciones", "Lección oral: Magnitudes físicas y vectores",            "LECCION_ORAL"),
        ("FIS", "Talleres",  "Taller: Laboratorio de caída libre",                     "TALLER"),
        # Química
        ("QUI", "Tareas",    "Tarea 1: Tabla periódica y propiedades de los elementos","TAREA"),
        ("QUI", "Lecciones", "Lección oral: Estructura atómica y orbitales",           "LECCION_ORAL"),
        ("QUI", "Talleres",  "Taller: Nomenclatura de compuestos inorgánicos",         "TALLER"),
        # Biología
        ("BIO", "Tareas",    "Tarea 1: Estructura celular eucariota y procariota",     "TAREA"),
        ("BIO", "Lecciones", "Lección oral: División celular – mitosis y meiosis",     "LECCION_ORAL"),
        ("BIO", "Talleres",  "Taller: Observación de células al microscopio",         "TALLER"),
        # Lengua y Literatura
        ("LEN", "Tareas",    "Tarea 1: Análisis de texto narrativo (cuento)",          "TAREA"),
        ("LEN", "Lecciones", "Lección oral: Figuras literarias y recursos estilísticos","LECCION_ORAL"),
        ("LEN", "Talleres",  "Taller: Producción de texto argumentativo",              "TALLER"),
        # Inglés
        ("ING", "Tareas",    "Task 1: Reading comprehension – short stories",         "TAREA"),
        ("ING", "Tareas",    "Task 2: Writing – formal email",                        "TAREA"),
        ("ING", "Lecciones", "Oral lesson: Present perfect and past simple",          "LECCION_ORAL"),
        ("ING", "Talleres",  "Workshop: Listening and speaking – daily routines",     "TALLER"),
        # Historia y Ciencias Sociales
        ("SOC", "Tareas",    "Tarea 1: Culturas precolombinas del Ecuador",            "TAREA"),
        ("SOC", "Lecciones", "Lección oral: Conquista española y colonia",             "LECCION_ORAL"),
        ("SOC", "Talleres",  "Taller: Línea del tiempo – historia ecuatoriana",       "TALLER"),
        # Filosofía
        ("FIL", "Tareas",    "Tarea 1: El pensamiento presocrático",                  "TAREA"),
        ("FIL", "Lecciones", "Lección oral: Sócrates, Platón y Aristóteles",          "LECCION_ORAL"),
        ("FIL", "Talleres",  "Taller: Debate filosófico – ética y virtud",            "TALLER"),
        # Educación Física
        ("EDU_FIS", "Tareas",    "Informe 1: Calentamiento y vuelta a la calma",          "TAREA"),
        ("EDU_FIS", "Talleres",  "Taller: Atletismo – técnica de carrera",               "TALLER"),
        # Educación Cultural y Artística
        ("EDU_ART", "Tareas",    "Tarea 1: Historia del arte – Renacimiento",            "TAREA"),
        ("EDU_ART", "Talleres",  "Taller: Técnicas mixtas – collage y acuarela",         "TALLER"),
    ],
    "T2-2526": [
        ("MAT", "Tareas",    "Tarea 3: Trigonometría básica y razones trigonométricas",  "TAREA"),
        ("MAT", "Tareas",    "Tarea 4: Geometría analítica – circunferencia",            "TAREA"),
        ("MAT", "Lecciones", "Lección oral: Funciones trigonométricas inversas",         "LECCION_ORAL"),
        ("MAT", "Talleres",  "Taller: Resolución de triángulos (Ley de senos y cosenos)","TALLER"),

        ("FIS", "Tareas",    "Tarea 2: Dinámica – Leyes de Newton",                      "TAREA"),
        ("FIS", "Lecciones", "Lección oral: Trabajo, energía y potencia",                "LECCION_ORAL"),
        ("FIS", "Talleres",  "Taller: Laboratorio de fuerza y masa",                     "TALLER"),

        ("QUI", "Tareas",    "Tarea 2: Reacciones químicas y estequiometría",            "TAREA"),
        ("QUI", "Lecciones", "Lección oral: Tipos de enlace químico",                    "LECCION_ORAL"),
        ("QUI", "Talleres",  "Taller: Laboratorio de reacciones ácido-base",             "TALLER"),

        ("BIO", "Tareas",    "Tarea 2: Genética mendeliana y leyes de Mendel",           "TAREA"),
        ("BIO", "Lecciones", "Lección oral: ADN, ARN y síntesis proteica",               "LECCION_ORAL"),
        ("BIO", "Talleres",  "Taller: Resolución de problemas genéticos (cuadros de Punnett)","TALLER"),

        ("LEN", "Tareas",    "Tarea 2: Análisis del discurso poético",                   "TAREA"),
        ("LEN", "Lecciones", "Lección oral: Literatura hispanoamericana del siglo XX",   "LECCION_ORAL"),
        ("LEN", "Talleres",  "Taller: Escritura creativa – microrrelato",                "TALLER"),

        ("ING", "Tareas",    "Task 3: Reading comprehension – news articles",            "TAREA"),
        ("ING", "Tareas",    "Task 4: Writing – opinion paragraph",                     "TAREA"),
        ("ING", "Lecciones", "Oral lesson: Conditional sentences (types 1 and 2)",      "LECCION_ORAL"),
        ("ING", "Talleres",  "Workshop: Debate – environmental issues",                 "TALLER"),

        ("SOC", "Tareas",    "Tarea 2: Independencia del Ecuador y Gran Colombia",       "TAREA"),
        ("SOC", "Lecciones", "Lección oral: Período republicano del Ecuador (siglo XIX)","LECCION_ORAL"),
        ("SOC", "Talleres",  "Taller: Análisis de fuentes históricas primarias",        "TALLER"),

        ("FIL", "Tareas",    "Tarea 2: Filosofía medieval – escolástica y teología",    "TAREA"),
        ("FIL", "Lecciones", "Lección oral: Descartes, Kant y el racionalismo",         "LECCION_ORAL"),
        ("FIL", "Talleres",  "Taller: Ensayo filosófico – libertad y determinismo",     "TALLER"),

        ("EDU_FIS", "Tareas",    "Informe 2: Fundamentos del deporte colectivo",         "TAREA"),
        ("EDU_FIS", "Talleres",  "Taller: Baloncesto – técnica y reglas de juego",      "TALLER"),

        ("EDU_ART", "Tareas",    "Tarea 2: Análisis de obra artística contemporánea",   "TAREA"),
        ("EDU_ART", "Talleres",  "Taller: Diseño gráfico – composición y color",        "TALLER"),
    ],
    "T3-2526": [
        ("MAT", "Tareas",    "Tarea 5: Estadística descriptiva y medidas de tendencia central","TAREA"),
        ("MAT", "Tareas",    "Tarea 6: Probabilidad clásica y frecuencial",              "TAREA"),
        ("MAT", "Lecciones", "Lección oral: Distribuciones de probabilidad",             "LECCION_ORAL"),
        ("MAT", "Talleres",  "Proyecto trimestral Matemática: encuesta y análisis estadístico","PROYECTO"),

        ("FIS", "Tareas",    "Tarea 3: Electrostática y Ley de Coulomb",                 "TAREA"),
        ("FIS", "Lecciones", "Lección oral: Circuitos eléctricos y Ley de Ohm",         "LECCION_ORAL"),
        ("FIS", "Talleres",  "Proyecto trimestral Física: construcción de circuito básico","PROYECTO"),

        ("QUI", "Tareas",    "Tarea 3: Cinética química y equilibrio químico",           "TAREA"),
        ("QUI", "Lecciones", "Lección oral: Soluciones y concentraciones",               "LECCION_ORAL"),
        ("QUI", "Talleres",  "Proyecto trimestral Química: análisis de muestra de agua", "PROYECTO"),

        ("BIO", "Tareas",    "Tarea 3: Ecosistemas y cadenas tróficas",                  "TAREA"),
        ("BIO", "Lecciones", "Lección oral: Evolución y teoría darwiniana",              "LECCION_ORAL"),
        ("BIO", "Talleres",  "Proyecto trimestral Biología: estudio de biodiversidad local","PROYECTO"),

        ("LEN", "Tareas",    "Tarea 3: Análisis de obra teatral latinoamericana",        "TAREA"),
        ("LEN", "Lecciones", "Lección oral: Oratoria y técnicas de presentación",       "LECCION_ORAL"),
        ("LEN", "Talleres",  "Proyecto trimestral Lengua: compilación de textos propios","PROYECTO"),

        ("ING", "Tareas",    "Task 5: Reading comprehension – academic texts",           "TAREA"),
        ("ING", "Tareas",    "Task 6: Writing – argumentative essay",                   "TAREA"),
        ("ING", "Lecciones", "Oral lesson: Passive voice and reported speech",          "LECCION_ORAL"),
        ("ING", "Talleres",  "Final project: Oral presentation – global issues",        "PROYECTO"),

        ("SOC", "Tareas",    "Tarea 3: Ecuador contemporáneo – economía y sociedad",    "TAREA"),
        ("SOC", "Lecciones", "Lección oral: Globalización y desafíos del siglo XXI",   "LECCION_ORAL"),
        ("SOC", "Talleres",  "Proyecto trimestral Sociales: investigación de campo",   "PROYECTO"),

        ("FIL", "Tareas",    "Tarea 3: Filosofía contemporánea – existencialismo",      "TAREA"),
        ("FIL", "Lecciones", "Lección oral: Ética aplicada y dilemas morales",         "LECCION_ORAL"),
        ("FIL", "Talleres",  "Proyecto trimestral Filosofía: ensayo de postura ética", "PROYECTO"),

        ("EDU_FIS", "Tareas",    "Informe 3: Plan personal de actividad física",        "TAREA"),
        ("EDU_FIS", "Talleres",  "Demostración deportiva final – atletismo o deporte colectivo","EXPOSICION"),

        ("EDU_ART", "Tareas",    "Tarea 3: Apreciación de obra musical ecuatoriana",   "TAREA"),
        ("EDU_ART", "Talleres",  "Exposición artística final – muestra de trabajos del año","EXPOSICION"),
    ],
}

# Distribución de notas realista: mayoría aprobando, algunos en riesgo
# Pesos: [4,5,6,7,8,9,10,10,9,8,7,6,5] → concentrado en 6-9
_NOTA_POOL = [
    Decimal("3.00"), Decimal("4.00"), Decimal("4.50"),
    Decimal("5.00"), Decimal("5.50"), Decimal("6.00"),
    Decimal("6.50"), Decimal("7.00"), Decimal("7.00"),
    Decimal("7.50"), Decimal("8.00"), Decimal("8.00"),
    Decimal("8.50"), Decimal("9.00"), Decimal("9.00"),
    Decimal("9.50"), Decimal("10.00"),
]

# Incidentes conductuales con descripciones realistas
INCIDENTES_DESCRIPCION = {
    "PERTURBACION": [
        "Habló en voz alta interrumpiendo la explicación del docente.",
        "Uso de celular durante la clase pese a indicaciones previas.",
        "Generó desorden al cambiar de sitio sin autorización.",
    ],
    "IRRESPETO": [
        "Hizo comentarios hirientes sobre el trabajo de un compañero.",
        "Se negó a trabajar en grupo generando tensión en el equipo.",
    ],
    "INASISTENCIA": [
        "Registra tres ausencias injustificadas consecutivas al inicio del trimestre.",
        "Acumula cinco tardanzas en el mes sin justificación presentada.",
    ],
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Pool dinámico de estudiantes y representantes para simulación multianual
STUDENT_POOL = []
REPRESENTATIVE_POOL = []

NOMBRES_EST = [
    "Sebastián Andrés", "Camila Valentina", "Diego Alejandro", "Gabriela Mishell",
    "Mateo Nicolás", "Andrea Sofía", "Andrés Mauricio", "Valeria Nicole",
    "Juan Pablo", "Paola Estefanía", "Kevin Steeven", "María Fernanda",
    "Luis Fernando", "Priscila Marisol", "Emilio Javier", "Natalia Daniela",
    "Pablo Rodrigo", "Karla Alejandra", "Bryan Stalyn", "Alejandra Pamela",
    "Cristian José", "Melanie Yoselin", "Ronaldo Jesús", "Carolina Liseth",
    "Daniel Esteban", "Sofía Lorena", "Alejandro René", "Lucía Fernanda",
    "Javier Eduardo", "Elena Margarita"
]

APELLIDOS = [
    "Almeida", "Burbano", "Córdova", "Delgado", "Espinoza", "Flores", "García", "Herrera",
    "Intriago", "Jiménez", "Lara", "Morales", "Naranjo", "Ortega", "Peña", "Quito",
    "Romero", "Samaniego", "Tapia", "Urgiles", "Vargas", "Washburn", "Yánez", "Zambrano",
    "Castro", "Cevallos", "Mendoza", "Palacios", "Salazar", "Vega", "Astudillo", "Rosero",
    "Cárdenas", "Montenegro", "Aguilar", "Bravo", "Freire", "Loor", "Montoya", "Zamora"
]

NOMBRES_REP = [
    "Roberto Carlos", "Gloria Esperanza", "Nelson Patricio", "Rosa Amparito", "Freddy Bolívar",
    "Silvia Marisol", "Marco Antonio", "Isabel Rocío", "Oswaldo Ramiro", "Carmen Auxiliadora",
    "Leonidas Raúl", "Verónica Susana", "Blanca Noemí", "Gonzalo Efraín", "Alexandra Paola",
    "Víctor Hugo", "Martha Cecilia", "César Augusto", "Gladys María", "Wilson René"
]

# Inicializar un generador de aleatoriedad local
local_rand = random.Random(2025)

# Generar 120 alumnos y representantes únicos
for i in range(1, 121):
    names = local_rand.choice(NOMBRES_EST)
    last_names = f"{local_rand.choice(APELLIDOS)} {local_rand.choice(APELLIDOS)}"
    doc_num = f"091020{i:04d}"
    birth_date = date(2009 + (i % 3), local_rand.randint(1, 12), local_rand.randint(1, 28))
    
    student_tag = f"est_{i:03d}"
    
    rep_names = local_rand.choice(NOMBRES_REP)
    rep_last_names = f"{last_names.split()[0]} {local_rand.choice(APELLIDOS)}"
    rep_doc = f"090010{i:04d}"
    rep_birth = date(1975 + (i % 10), local_rand.randint(1, 12), local_rand.randint(1, 28))
    rep_tag = f"rep_{i:03d}"
    kinship = local_rand.choice(["PADRE", "MADRE", "PADRE", "MADRE", "TUTOR"])
    
    STUDENT_POOL.append({
        "tag": student_tag,
        "document_number": doc_num,
        "names": names,
        "last_names": last_names,
        "birth_date": birth_date,
    })
    
    REPRESENTATIVE_POOL.append({
        "tag": rep_tag,
        "document_number": rep_doc,
        "names": rep_names,
        "last_names": rep_last_names,
        "birth_date": rep_birth,
        "kinship_code": kinship,
        "students": [student_tag]
    })

# Definición de años escolares e históricos
SCHOOL_YEARS_DATA = [
    {
        "name": "2023-2024",
        "start_date": date(2023, 9, 1),
        "end_date":   date(2024, 6, 30),
        "is_active":  False,
        "trimestres": [
            {"code": "T1-2324", "name": "Primer Trimestre", "start_date": date(2023, 9, 1), "end_date": date(2023, 11, 30), "weight": Decimal("33.33")},
            {"code": "T2-2324", "name": "Segundo Trimestre", "start_date": date(2023, 12, 1), "end_date": date(2024, 3, 15), "weight": Decimal("33.33")},
            {"code": "T3-2324", "name": "Tercer Trimestre", "start_date": date(2024, 3, 18), "end_date": date(2024, 6, 30), "weight": Decimal("33.34")},
        ]
    },
    {
        "name": "2024-2025",
        "start_date": date(2024, 9, 1),
        "end_date":   date(2025, 6, 30),
        "is_active":  False,
        "trimestres": [
            {"code": "T1-2425", "name": "Primer Trimestre", "start_date": date(2024, 9, 1), "end_date": date(2024, 11, 30), "weight": Decimal("33.33")},
            {"code": "T2-2425", "name": "Segundo Trimestre", "start_date": date(2024, 12, 1), "end_date": date(2025, 3, 14), "weight": Decimal("33.33")},
            {"code": "T3-2425", "name": "Tercer Trimestre", "start_date": date(2025, 3, 17), "end_date": date(2025, 6, 30), "weight": Decimal("33.34")},
        ]
    },
    {
        "name": "2025-2026",
        "start_date": date(2025, 9, 1),
        "end_date":   date(2026, 7, 31),
        "is_active":  True,
        "trimestres": [
            {"code": "T1-2526", "name": "Primer Trimestre", "start_date": date(2025, 9, 1), "end_date": date(2025, 11, 30), "weight": Decimal("33.33")},
            {"code": "T2-2526", "name": "Segundo Trimestre", "start_date": date(2025, 12, 1), "end_date": date(2026, 3, 20), "weight": Decimal("33.33")},
            {"code": "T3-2526", "name": "Tercer Trimestre", "start_date": date(2026, 3, 23), "end_date": date(2026, 7, 31), "weight": Decimal("33.34")},
        ]
    }
]

class Command(BaseCommand):
    help = "Siembra datos de prueba multianuales coherentes con el paralelo C y soporte para ML"

    @staticmethod
    def _sync_is_active(obj, is_active, created):
        """Alinea is_active en re-ejecuciones (años históricos deben quedar inactivos)."""
        if not created and obj.is_active != is_active:
            obj.is_active = is_active
            obj.save(update_fields=["is_active"])

    def handle(self, *args, **options):
        random.seed(RANDOM_SEED)  # garantizar reproducibilidad
        local_rand = random.Random(RANDOM_SEED)

        self._seed_catalogs()
        self._seed_permissions_and_roles()

        grade_bgu1, grade_bgu2 = self._create_grades()
        subjects = self._create_subjects()
        configs_bgu1 = self._create_subject_configs(subjects, grade_bgu1)
        configs_bgu2 = self._create_subject_configs(subjects, grade_bgu2)

        admin_users = self._create_admin_users()
        doc_users = self._create_docentes()
        self._assign_roles(admin_users, doc_users)

        self.stdout.write("  -> Creando pool global de estudiantes...")
        est_users = {}
        students = {}
        est_role = Role.objects.get(code="ESTUDIANTE")
        for e in STUDENT_POOL:
            apellido_slug = e["last_names"].split()[0].lower()
            for a, b in [("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("ñ","n")]:
                apellido_slug = apellido_slug.replace(a, b)
            email    = f"est.{apellido_slug}.{e['tag']}@uetest.edu.ec"
            password = f"Est.{e['last_names'].split()[0]}2025!"
            u = self._make_user(
                document_number=e["document_number"],
                names=e["names"],
                last_names=e["last_names"],
                email=email,
                password=password,
                birth_date=e["birth_date"],
            )
            est_users[e["tag"]] = u
            UserRole.objects.get_or_create(user=u, role=est_role)
            student, _ = Student.objects.get_or_create(
                student_code=f"BGU-{e['document_number'][-6:]}",
                defaults={
                    "user":              u,
                    "is_active":         True,
                    "has_special_needs": e["tag"] == "est_001",
                },
            )
            students[e["tag"]] = student

        self.stdout.write("  -> Creando pool global de representantes...")
        rep_users = {}
        rep_role = Role.objects.get(code="REPRESENTANTE")
        for r in REPRESENTATIVE_POOL:
            apellido_slug = r["last_names"].split()[0].lower()
            for a, b in [("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("ñ","n")]:
                apellido_slug = apellido_slug.replace(a, b)
            email    = f"rep.{apellido_slug}@uetest.edu.ec"
            password = f"Rep.{r['last_names'].split()[0]}2025!"
            u = self._make_user(
                document_number=r["document_number"],
                names=r["names"],
                last_names=r["last_names"],
                email=email,
                password=password,
                birth_date=r["birth_date"],
            )
            rep_users[r["tag"]] = u
            UserRole.objects.get_or_create(user=u, role=rep_role)

            kinship = Kinship.objects.get(code=r["kinship_code"])
            for idx, student_tag in enumerate(r["students"]):
                stud = students[student_tag]
                StudentRepresentative.objects.get_or_create(
                    student=stud,
                    user=u,
                    defaults={
                        "kinship":                kinship,
                        "is_primary":             True,
                        "receives_notifications": True,
                        "is_active":              True,
                        "emergency_contact":      idx == 0,
                    },
                )

        student_states = {e["tag"]: {"last_grade": None, "last_status": None, "repeat_count": 0} for e in STUDENT_POOL}
        free_students = [e["tag"] for e in STUDENT_POOL]
        current_enrollments = {}

        for sy_data in SCHOOL_YEARS_DATA:
            year_is_active = sy_data["is_active"]

            self.stdout.write(f"\n==================================================")
            self.stdout.write(f"PROCESANDO AÑO LECTIVO: {sy_data['name']}")
            self.stdout.write(f"==================================================")

            school_year, created_sy = SchoolYear.objects.get_or_create(
                start_date=sy_data["start_date"],
                defaults={
                    "end_date":   sy_data["end_date"],
                    "is_active":  sy_data["is_active"],
                },
            )
            if not created_sy:
                sy_updates = {}
                if school_year.end_date != sy_data["end_date"]:
                    sy_updates["end_date"] = sy_data["end_date"]
                expected_active = sy_data["is_active"]
                if school_year.is_active != expected_active:
                    sy_updates["is_active"] = expected_active
                if sy_updates:
                    for field, value in sy_updates.items():
                        setattr(school_year, field, value)
                    school_year.save(update_fields=list(sy_updates.keys()))
            elif not sy_data["is_active"]:
                school_year.is_active = False
                school_year.save(update_fields=["is_active"])

            sections = {}
            for grade_code, grade in [("BGU_1RO", grade_bgu1), ("BGU_2DO", grade_bgu2)]:
                sections[grade_code] = {}
                for parallel in ("A", "B", "C"):
                    code = f"{grade_code}_{parallel}_{sy_data['name'].replace('-', '')}"
                    obj, created = Section.objects.get_or_create(
                        code=code,
                        defaults={
                            "school_year":    school_year,
                            "academic_grade": grade,
                            "parallel":       parallel,
                            "capacity":       35,
                            "is_active":      year_is_active,
                        },
                    )
                    self._sync_is_active(obj, year_is_active, created)
                    sections[grade_code][parallel] = obj

            offerings = {}
            for grade_code, configs in [("BGU_1RO", configs_bgu1), ("BGU_2DO", configs_bgu2)]:
                for parallel, section in sections[grade_code].items():
                    for code, cfg in configs.items():
                        obj, created = SubjectOffering.objects.get_or_create(
                            section=section,
                            subject_academic_config=cfg,
                            defaults={"is_active": year_is_active},
                        )
                        self._sync_is_active(obj, year_is_active, created)
                        offerings[(grade_code, code, parallel)] = obj

            period_type = PeriodType.objects.get(code="TRIMESTRE")
            periods = []
            for t in sy_data["trimestres"]:
                obj, created = AcademicPeriod.objects.get_or_create(
                    school_year=school_year,
                    code=t["code"],
                    defaults={
                        "name":               t["name"],
                        "start_date":         t["start_date"],
                        "end_date":           t["end_date"],
                        "period_type":        period_type,
                        "is_regular_period":  True,
                        "is_active":          year_is_active,
                        "year_weight":        t["weight"],
                        "grades_locked":      not year_is_active,
                    },
                )
                if not created:
                    updates = {}
                    if obj.is_active != year_is_active:
                        updates["is_active"] = year_is_active
                    expected_locked = not year_is_active
                    if obj.grades_locked != expected_locked:
                        updates["grades_locked"] = expected_locked
                    for date_field in ("start_date", "end_date"):
                        expected = t[date_field]
                        if getattr(obj, date_field) != expected:
                            updates[date_field] = expected
                    if updates:
                        for field, value in updates.items():
                            setattr(obj, field, value)
                        obj.save(update_fields=list(updates.keys()))
                periods.append(obj)

            teacher_map = {}
            for d in DOCENTES:
                user = doc_users[d["tag"]]
                scode = d["subject_code"]
                for grade_code in ("BGU_1RO", "BGU_2DO"):
                    for parallel in ("A", "B", "C"):
                        key = (grade_code, scode, parallel)
                        offering = offerings.get(key)
                        if not offering:
                            continue
                        tss, created = TeacherSubjectSection.objects.get_or_create(
                            user=user,
                            subject_offering=offering,
                            defaults={"is_active": year_is_active},
                        )
                        self._sync_is_active(tss, year_is_active, created)
                        teacher_map[key] = tss

            def _get_swapped_times(start_time, end_time):
                # Shift A
                if start_time == _t(7, 0): return _t(8, 30), _t(9, 15)
                if start_time == _t(7, 45): return _t(9, 15), _t(10, 0)
                if start_time == _t(8, 30): return _t(7, 0), _t(7, 45)
                if start_time == _t(9, 15): return _t(7, 45), _t(8, 30)
                # Shift B
                if start_time == _t(10, 15): return _t(11, 45), _t(12, 30)
                if start_time == _t(11, 0): return _t(12, 30), _t(13, 15)
                if start_time == _t(11, 45): return _t(10, 15), _t(11, 0)
                if start_time == _t(12, 30): return _t(11, 0), _t(11, 45)
                return start_time, end_time

            count_schedules = 0
            for (scode, parallel, day, start, end) in SCHEDULE_SLOTS:
                for grade_code in ("BGU_1RO", "BGU_2DO"):
                    if grade_code == "BGU_2DO":
                        actual_start, actual_end = _get_swapped_times(start, end)
                    else:
                        actual_start, actual_end = start, end

                    tss = teacher_map.get((grade_code, scode, parallel))
                    if tss:
                        cs, created = ClassSchedule.objects.get_or_create(
                            teacher_subject_section=tss,
                            day_of_week=day,
                            start_time=actual_start,
                            defaults={"end_time": actual_end, "is_active": year_is_active},
                        )
                        if not created and (cs.is_active != year_is_active or cs.end_time != actual_end):
                            cs.is_active = year_is_active
                            cs.end_time = actual_end
                            cs.save()
                        count_schedules += 1

                    if parallel == "A":
                        tss_c = teacher_map.get((grade_code, scode, "C"))
                        if tss_c:
                            c_start = (datetime.datetime.combine(datetime.date.today(), actual_start) + datetime.timedelta(hours=6, minutes=30)).time()
                            c_end = (datetime.datetime.combine(datetime.date.today(), actual_end) + datetime.timedelta(hours=6, minutes=30)).time()
                            cs_c, created_c = ClassSchedule.objects.get_or_create(
                                teacher_subject_section=tss_c,
                                day_of_week=day,
                                start_time=c_start,
                                defaults={"end_time": c_end, "is_active": year_is_active},
                            )
                            if not created_c and (cs_c.is_active != year_is_active or cs_c.end_time != c_end):
                                cs_c.is_active = year_is_active
                                cs_c.end_time = c_end
                                cs_c.save()
                            count_schedules += 1
            self.stdout.write(f"  [OK] Horarios creados para el año: {count_schedules}")

            current_enrollments = {}

            # --- Matrículas 2do BGU ---
            passed_1ro = [tag for tag, state in student_states.items() if state["last_grade"] == "BGU_1RO" and state["last_status"] == "PASSED"]
            local_rand.shuffle(passed_1ro)

            for idx, tag in enumerate(passed_1ro[:36]):
                parallel = ("A", "B", "C")[idx % 3]
                sec = sections["BGU_2DO"][parallel]
                stud = students[tag]
                enroll, _ = Enrollment.objects.get_or_create(
                    student=stud,
                    section=sec,
                    defaults={"enrollment_status": "ACT", "is_repeat": False}
                )
                current_enrollments[tag] = enroll
                student_states[tag]["last_grade"] = "BGU_2DO"
                student_states[tag]["last_status"] = None

            # --- Matrículas 1ro BGU ---
            repeaters_1ro = [tag for tag, state in student_states.items() if state["last_grade"] == "BGU_1RO" and state["last_status"] == "FAILED"]
            needed_new = 36 - len(repeaters_1ro)
            new_intake = []
            if needed_new > 0:
                new_intake = free_students[:needed_new]
                free_students = free_students[needed_new:]

            intake_1ro = repeaters_1ro + new_intake
            local_rand.shuffle(intake_1ro)

            for idx, tag in enumerate(intake_1ro[:36]):
                parallel = ("A", "B", "C")[idx % 3]
                sec = sections["BGU_1RO"][parallel]
                stud = students[tag]
                is_rep = tag in repeaters_1ro
                enroll, _ = Enrollment.objects.get_or_create(
                    student=stud,
                    section=sec,
                    defaults={"enrollment_status": "ACT", "is_repeat": is_rep}
                )
                current_enrollments[tag] = enroll
                student_states[tag]["last_grade"] = "BGU_1RO"
                student_states[tag]["last_status"] = None
                if is_rep:
                    student_states[tag]["repeat_count"] += 1

            self.stdout.write(f"  [OK] Matrículas generadas: {len(current_enrollments)} (1ro BGU: {len(intake_1ro)}, 2do BGU: {len(passed_1ro[:36])})")

            failing_students = set()
            medium_risk_students = set()
            
            students_1ro = [tag for tag in current_enrollments if student_states[tag]["last_grade"] == "BGU_1RO"]
            num_fail_1ro = int(len(students_1ro) * 0.15)
            num_med_1ro = int(len(students_1ro) * 0.15)
            sampled_1ro = local_rand.sample(students_1ro, num_fail_1ro + num_med_1ro)
            failing_students.update(sampled_1ro[:num_fail_1ro])
            medium_risk_students.update(sampled_1ro[num_fail_1ro:])

            students_2do = [tag for tag in current_enrollments if student_states[tag]["last_grade"] == "BGU_2DO"]
            num_fail_2do = int(len(students_2do) * 0.15)
            num_med_2do = int(len(students_2do) * 0.15)
            sampled_2do = local_rand.sample(students_2do, num_fail_2do + num_med_2do)
            failing_students.update(sampled_2do[:num_fail_2do])
            medium_risk_students.update(sampled_2do[num_fail_2do:])

            for tag in current_enrollments:
                if tag in failing_students:
                    student_states[tag]["last_status"] = "FAILED"
                else:
                    student_states[tag]["last_status"] = "PASSED"

            self._generate_attendance_for_sy(current_enrollments, teacher_map, periods, failing_students, medium_risk_students)
            self._generate_conduct_incidents_for_sy(current_enrollments, periods, failing_students, medium_risk_students)

            grading_struct = self._create_grading_structure_for_sy(
                periods, offerings, year_is_active
            )
            self._create_evaluative_activities_for_sy(
                teacher_map, grading_struct, periods, year_is_active
            )
            self._create_student_notes_for_sy(current_enrollments, grading_struct, doc_users, failing_students, medium_risk_students)

            self._create_behavior_evaluations(current_enrollments, periods, admin_users)
            self._create_early_alerts(current_enrollments, periods, admin_users)
            self._create_risk_data_for_sy(current_enrollments, periods, failing_students, medium_risk_students)

        global ESTUDIANTES, REPRESENTANTES
        ESTUDIANTES = []
        for item in STUDENT_POOL:
            tag = item["tag"]
            stud_obj = students[tag]
            active_enroll = Enrollment.objects.filter(student=stud_obj, section__school_year__is_active=True).first()
            if active_enroll:
                ESTUDIANTES.append({
                    "tag": tag,
                    "document_number": stud_obj.user.person.document_number,
                    "names": stud_obj.user.person.names,
                    "last_names": stud_obj.user.person.last_names,
                    "parallel": active_enroll.section.parallel,
                    "birth_date": stud_obj.user.person.birth_date,
                })

        REPRESENTANTES = []
        for r in REPRESENTATIVE_POOL:
            active_students = [s_tag for s_tag in r["students"] if any(e["tag"] == s_tag for e in ESTUDIANTES)]
            if active_students:
                REPRESENTANTES.append({
                    "tag": r["tag"],
                    "document_number": r["document_number"],
                    "names": r["names"],
                    "last_names": r["last_names"],
                    "birth_date": r["birth_date"],
                    "kinship_code": r["kinship_code"],
                    "students": active_students
                })

        active_sy = SchoolYear.objects.filter(is_active=True).first()
        active_sections = Section.objects.filter(school_year=active_sy)
        active_periods = AcademicPeriod.objects.filter(school_year=active_sy)
        active_students_objs = [students[e["tag"]] for e in ESTUDIANTES]
        active_enrollments = {e["tag"]: current_enrollments[e["tag"]] for e in ESTUDIANTES}

        self._print_summary(
            active_sy, active_sections, active_periods, active_students_objs, active_enrollments,
            admin_users, doc_users, rep_users, est_users
        )

    def _seed_catalogs(self):
        self.stdout.write("  -> Sembrando catálogos base...")
        call_command("seed_catalogs")

    def _seed_permissions_and_roles(self):
        self.stdout.write("  -> Sembrando permisos y roles...")
        call_command("seed_permissions")

    def _create_grades(self):
        nivel_bgu = AcademicLevel.objects.get(code="BGU")
        sublevel, _ = AcademicSublevel.objects.get_or_create(
            code="BACHILLERATO",
            defaults={
                "name":           "Bachillerato General Unificado",
                "description":    "Educación media superior (1ro a 3ro BGU)",
                "academic_level": nivel_bgu,
                "is_active":      True,
            },
        )
        grade_bgu1, _ = AcademicGrade.objects.get_or_create(
            code="BGU_1RO",
            defaults={
                "name":              "1ro BGU",
                "academic_sublevel": sublevel,
                "is_active":         True,
            },
        )
        grade_bgu2, _ = AcademicGrade.objects.get_or_create(
            code="BGU_2DO",
            defaults={
                "name":              "2do BGU",
                "academic_sublevel": sublevel,
                "is_active":         True,
            },
        )
        self.stdout.write(f"  [OK] Grados creados: 1ro BGU, 2do BGU")
        return grade_bgu1, grade_bgu2

    def _create_subjects(self):
        objs = {}
        for code, name, _ in MATERIAS_BGU:
            obj, _ = Subject.objects.get_or_create(
                code=code,
                defaults={"name": name, "is_active": True},
            )
            objs[code] = obj
        self.stdout.write(f"  [OK] Asignaturas verificadas: {len(objs)}")
        return objs

    def _create_subject_configs(self, subjects, grade):
        configs = {}
        for code, _, weekly_hours in MATERIAS_BGU:
            subj = subjects[code]
            cfg, _ = SubjectAcademicConfig.objects.get_or_create(
                subject=subj,
                academic_grade=grade,
                defaults={
                    "weekly_hours": weekly_hours,
                    "is_required":  True,
                    "is_active":    True,
                },
            )
            configs[code] = cfg
        self.stdout.write(f"  [OK] Configuraciones de asignatura para {grade.name}: {len(configs)}")
        return configs

    def _make_user(self, document_number, names, last_names, email, password,
                   birth_date, is_superuser=False):
        doc_type = DocumentType.objects.get(code="CC")
        person, _ = Person.objects.get_or_create(
            document_number=document_number,
            defaults={
                "document_type": doc_type,
                "names":         names,
                "last_names":    last_names,
                "email":         email,
                "birth_date":    birth_date,
                "is_active":     True,
                "phone":         f"+5939{document_number[-8:]}",
            },
        )
        username = User.generate_username(names, last_names)
        kwargs = {
            "username":   username,
            "is_active":  True,
            "must_change_password": False,
        }
        if is_superuser:
            kwargs.update({"is_staff": True, "is_superuser": True})
        user, created = User.objects.get_or_create(person=person, defaults=kwargs)
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
        return user

    def _create_admin_users(self):
        users = {}
        for item in ADMIN_USERS:
            u = self._make_user(
                document_number=item["document_number"],
                names=item["names"],
                last_names=item["last_names"],
                email=item["email"],
                password=item["password"],
                birth_date=item["birth_date"],
                is_superuser=item.get("is_superuser", False),
            )
            users[item["tag"]] = u
            self.stdout.write(f"  [OK] Admin: {item['email']}")
        return users

    def _create_docentes(self):
        users = {}
        for d in DOCENTES:
            apellido_slug = d["last_names"].split()[0].lower()
            for a, b in [("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("ñ","n")]:
                apellido_slug = apellido_slug.replace(a, b)
            email    = f"doc.{apellido_slug}@uetest.edu.ec"
            password = f"Doc.{d['last_names'].split()[0]}2025!"
            u = self._make_user(
                document_number=d["document_number"],
                names=d["names"],
                last_names=d["last_names"],
                email=email,
                password=password,
                birth_date=d["birth_date"],
            )
            users[d["tag"]] = u
            self.stdout.write(f"  [OK] Docente ({d['subject_code']}): {email}")
        return users

    def _assign_roles(self, admin_users, doc_users):
        role_map = {
            "admin":     None,
            "director":  "DIRECTOR",
            "consejero": "CONSEJERO",
        }
        for tag, role_code in role_map.items():
            if not role_code:
                continue
            user = admin_users[tag]
            role = Role.objects.get(code=role_code)
            UserRole.objects.get_or_create(user=user, role=role)

        docente_role = Role.objects.get(code="DOCENTE")
        for user in doc_users.values():
            UserRole.objects.get_or_create(user=user, role=docente_role)
        self.stdout.write("  [OK] Roles asignados")

    def _generate_attendance_for_sy(self, enrollments, teacher_map, periods, failing_students, medium_risk_students):
        status_P = AttendanceStatus.objects.get(code="P")
        status_T = AttendanceStatus.objects.get(code="T")
        status_J = AttendanceStatus.objects.get(code="J")
        status_A = AttendanceStatus.objects.get(code="A")

        passing_pool = [status_P] * 92 + [status_T] * 5 + [status_J] * 2 + [status_A] * 1
        medium_pool  = [status_P] * 78 + [status_T] * 6 + [status_J] * 6 + [status_A] * 10
        failing_pool = [status_P] * 60 + [status_T] * 8 + [status_J] * 12 + [status_A] * 20

        schedules = ClassSchedule.objects.select_related("teacher_subject_section").all()
        attendance_to_create = []

        for period in periods:
            start_dt = period.start_date
            end_dt = _instructional_end_date(period)

            current_date = start_dt
            dates_by_weekday = {i: [] for i in range(1, 8)}
            while current_date <= end_dt:
                dates_by_weekday[current_date.isoweekday()].append(current_date)
                current_date += datetime.timedelta(days=1)

            for schedule in schedules:
                tss = schedule.teacher_subject_section
                if tss.subject_offering.section.school_year_id != period.school_year_id:
                    continue

                matching_enrollments = [
                    (est_tag, enrollment)
                    for est_tag, enrollment in enrollments.items()
                    if enrollment.section_id == tss.subject_offering.section_id
                ]

                dates = dates_by_weekday.get(schedule.day_of_week, [])
                for date_val in dates:
                    for est_tag, enrollment in matching_enrollments:
                        if est_tag in failing_students:
                            pool = failing_pool
                        elif est_tag in medium_risk_students:
                            pool = medium_pool
                        else:
                            pool = passing_pool
                        status = local_rand.choice(pool)
                        attendance_to_create.append(
                            Attendance(
                                enrollment=enrollment,
                                teacher_subject_section=tss,
                                class_schedule=schedule,
                                academic_period=period,
                                attendance_date=date_val,
                                attendance_status=status,
                                observation="",
                                sync_status="SYNCED",
                                sync_version=1,
                            )
                        )
        if attendance_to_create:
            Attendance.objects.bulk_create(attendance_to_create, batch_size=2000)
        self.stdout.write(f"  [OK] Asistencias generadas para el año: {len(attendance_to_create)}")

    def _generate_conduct_incidents_for_sy(self, enrollments, periods, failing_students, medium_risk_students):
        count = 0
        severity_leve = Severity.objects.get(code="LEVE")
        severity_mod  = Severity.objects.get(code="MODERADA")
        severity_grave  = Severity.objects.get(code="GRAVE")

        all_enrollments = list(enrollments.items())
        incident_data = list(INCIDENTES_DESCRIPCION.items())

        for period in periods:
            n_incidents = local_rand.randint(2, 4)
            targets = local_rand.sample(all_enrollments, min(n_incidents, len(all_enrollments)))
            for est_tag, enrollment in targets:
                inc_type_code, descriptions = local_rand.choice(incident_data)
                try:
                    inc_type  = IncidentType.objects.get(code=inc_type_code)
                    severity  = severity_mod if inc_type_code == "IRRESPETO" else severity_leve
                    desc      = local_rand.choice(descriptions)
                    instructional_end = _instructional_end_date(period)
                    max_day = (instructional_end - period.start_date).days
                    incident_date = period.start_date + datetime.timedelta(
                        days=local_rand.randint(5, min(45, max(5, max_day)))
                    )
                    incident_date = min(incident_date, instructional_end)
                    ConductIncident.objects.get_or_create(
                        enrollment=enrollment,
                        academic_period=period,
                        incident_date=incident_date,
                        incident_type=inc_type,
                        defaults={
                            "severity":          severity,
                            "description":       desc,
                            "family_notified":   local_rand.choice([True, False]),
                            "actions_taken":     "Diálogo con el estudiante.",
                            "sync_status":       "SYNCED",
                            "sync_version":      1,
                        },
                    )
                    count += 1
                except IncidentType.DoesNotExist:
                    pass

            failing_enrollments = [(tag, enroll) for tag, enroll in all_enrollments if tag in failing_students]
            if failing_enrollments:
                n_fails = local_rand.randint(1, min(3, len(failing_enrollments)))
                targets = local_rand.sample(failing_enrollments, n_fails)
                for est_tag, enrollment in targets:
                    try:
                        inc_type = IncidentType.objects.get(code="INASISTENCIA")
                        desc = "Falta de respeto o inasistencia reiterativa a clases."
                        instructional_end = _instructional_end_date(period)
                        max_day = (instructional_end - period.start_date).days
                        incident_date = period.start_date + datetime.timedelta(
                            days=local_rand.randint(5, min(45, max(5, max_day)))
                        )
                        incident_date = min(incident_date, instructional_end)
                        ConductIncident.objects.get_or_create(
                            enrollment=enrollment,
                            academic_period=period,
                            incident_date=incident_date,
                            incident_type=inc_type,
                            defaults={
                                "severity":          severity_grave,
                                "description":       desc,
                                "family_notified":   True,
                                "actions_taken":     "Derivación al DECE y llamado a representante.",
                                "sync_status":       "SYNCED",
                                "sync_version":      1,
                            },
                        )
                        count += 1
                    except IncidentType.DoesNotExist:
                        pass
        self.stdout.write(f"  [OK] Incidentes de conducta creados: {count}")

    def _create_grading_structure_for_sy(self, periods, offerings, year_is_active):
        result = {}
        components_meta = [
            ("Tareas",    Decimal("40.00")),
            ("Lecciones", Decimal("30.00")),
            ("Talleres",  Decimal("30.00")),
        ]
        for period in periods:
            for (grade_code, scode, parallel), offering in offerings.items():
                subject_name = offering.subject_academic_config.subject.name
                block_code = f"BLK_{period.code}_{grade_code}_{scode}_{parallel}"
                block, created = EvaluationBlock.objects.get_or_create(
                    code=block_code,
                    defaults={
                        "academic_period":   period,
                        "subject_offering":  offering,
                        "block_type":        "FORMATIVA",
                        "name":              f"Formativa {period.name} – {subject_name} {parallel}",
                        "weight_percentage": Decimal("100.00"),
                        "is_active":         year_is_active,
                    },
                )
                self._sync_is_active(block, year_is_active, created)
                comps = []
                for comp_name, weight in components_meta:
                    comp_code = f"{block_code}_{comp_name[:3].upper()}"
                    comp, created = BlockComponent.objects.get_or_create(
                        code=comp_code,
                        defaults={
                            "evaluation_block": block,
                            "name":             comp_name,
                            "internal_weight":  weight,
                            "is_active":        year_is_active,
                        },
                    )
                    self._sync_is_active(comp, year_is_active, created)
                    comps.append({"component": comp, "name": comp_name})
                result[(period.code, grade_code, scode, parallel)] = {
                    "block":    block,
                    "period":   period,
                    "offering": offering,
                    "comps":    comps,
                    "subject":  scode,
                }
        self.stdout.write(f"  [OK] Bloques de evaluación: {len(result)}")
        return result

    def _create_evaluative_activities_for_sy(
        self, teacher_map, grading_struct, periods, year_is_active
    ):
        count = 0
        for (period_code, grade_code, scode, parallel), structure in grading_struct.items():
            tss = teacher_map.get((grade_code, scode, parallel))
            if not tss:
                continue

            period = structure["period"]
            mapped_tri_code = period_code.split("-")[0]
            original_code_key = f"{mapped_tri_code}-2526"
            actividades = ACTIVIDADES_POR_TRIMESTRE.get(original_code_key, [])

            sub_actividades = [
                (sc, comp_name, title, atype_code)
                for (sc, comp_name, title, atype_code) in actividades
                if sc == scode
            ]

            comp_by_name = {c["name"]: c["component"] for c in structure["comps"]}
            instructional_end = _instructional_end_date(period)
            due_date = period.start_date + ((instructional_end - period.start_date) // 2)
            due_date = min(due_date, instructional_end)

            for (_, comp_name, title, atype_code) in sub_actividades:
                component = comp_by_name.get(comp_name)
                if not component:
                    continue
                try:
                    activity_type = ActivityType.objects.get(code=atype_code)
                except ActivityType.DoesNotExist:
                    activity_type = ActivityType.objects.get(code="TAREA")

                obj, created = EvaluativeActivity.objects.get_or_create(
                    block_component=component,
                    teacher_subject_section=tss,
                    title=f"{title} ({period.name})",
                    defaults={
                        "activity_type":   activity_type,
                        "max_score":       Decimal("10.00"),
                        "internal_weight": Decimal("100.00"),
                        "due_date":        due_date,
                        "is_active":       year_is_active,
                        "sync_status":     "SYNCED",
                        "sync_version":    1,
                    },
                )
                if not created and obj.due_date != due_date:
                    obj.due_date = due_date
                    obj.save(update_fields=["due_date"])
                self._sync_is_active(obj, year_is_active, created)
                if created:
                    count += 1
        self.stdout.write(f"  [OK] Actividades evaluativas: {count}")

    def _create_student_notes_for_sy(self, enrollments, grading_struct, doc_users, failing_students, medium_risk_students):
        count = 0
        docente_by_scode = {d["subject_code"]: d["tag"] for d in DOCENTES}

        passing_grade_pool = [7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0]
        medium_grade_pool  = [5.5, 6.0, 6.5, 7.0, 7.5, 8.0]
        failing_grade_pool = [2.0, 3.5, 4.0, 5.0, 5.5, 6.0, 6.5]

        with skip_period_summary_recalc():
            for (period_code, grade_code, scode, parallel), structure in grading_struct.items():
                doc_tag = docente_by_scode.get(scode)
                if not doc_tag:
                    continue
                docente = doc_users.get(doc_tag)
                if not docente:
                    continue

                for comp in structure["comps"]:
                    component = comp["component"]
                    activities = list(component.activities.all())
                    if not activities:
                        continue

                    for est_tag, enrollment in enrollments.items():
                        if enrollment.section_id != structure["offering"].section_id:
                            continue

                        if est_tag in failing_students:
                            pool = failing_grade_pool
                        elif est_tag in medium_risk_students:
                            pool = medium_grade_pool
                        else:
                            pool = passing_grade_pool
                        for activity in activities:
                            nota = local_rand.choice(pool)
                            _, created = StudentNote.objects.get_or_create(
                                enrollment=enrollment,
                                evaluative_activity=activity,
                                defaults={
                                    "grading_mode":       "NUMERIC",
                                    "numeric_score":      nota,
                                    "teacher_observation": "",
                                    "created_by":         docente,
                                    "modified_by":        docente,
                                    "sync_status":        "SYNCED",
                                    "sync_version":       1,
                                },
                            )
                            if created:
                                count += 1

        self.stdout.write(f"  [OK] Notas registradas para el año: {count}")

        for period in set(s["period"] for s in grading_struct.values()):
            ids = GradeCalculationService.calculate_all_for_period(period.id)
            if ids:
                self.stdout.write(
                    f"  [OK] Resúmenes recalculados – {period.name}: {len(ids)}"
                )

    def _create_behavior_evaluations(self, enrollments, periods, admin_users):
        count = 0
        consejero = admin_users.get("consejero")
        for enrollment in enrollments.values():
            for period in periods:
                try:
                    evaluation = BehaviorEvaluationService.calculate_behavior_evaluation(
                        enrollment, period
                    )
                    if evaluation.final_scale is None:
                        evaluation.final_scale = evaluation.calculated_scale
                    evaluation.created_by     = consejero
                    evaluation.evaluated_by   = consejero
                    evaluation.approved_by    = consejero
                    evaluation.approval_date  = period.end_date
                    evaluation.general_observation = (
                        "Evaluación de conducta generada al cierre del período."
                    )
                    evaluation.sync_status   = "SYNCED"
                    evaluation.sync_version  = 1
                    evaluation.save()
                    count += 1
                except Exception as e:
                    pass
        self.stdout.write(f"  [OK] Evaluaciones de conducta: {count}")

    def _create_early_alerts(self, enrollments, periods, admin_users):
        count = 0
        consejero   = admin_users.get("consejero")
        all_enroll  = list(enrollments.values())
        alert_types = [
            ("low_attendance",  "Porcentaje de asistencia por debajo del umbral mínimo (80%)."),
            ("failing_grades",  "Promedio acumulado inferior a 7 puntos en una o más asignaturas."),
            ("behavior_issues", "Registro de más de dos incidentes conductuales en el período."),
        ]

        for period in periods:
            targets = local_rand.sample(all_enroll, min(4, len(all_enroll)))
            for enrollment in targets:
                alert_type, description = local_rand.choice(alert_types)
                attended_at = datetime.datetime.combine(
                    _instructional_end_date(period),
                    datetime.time(16, 0, 0),
                    tzinfo=datetime.timezone.utc,
                )
                _, created = EarlyAlert.objects.get_or_create(
                    enrollment=enrollment,
                    academic_period=period,
                    alert_type=alert_type,
                    defaults={
                        "description":      description,
                        "urgency_level":    local_rand.choice(["low", "medium", "high"]),
                        "attended":         True,
                        "attended_by_user": consejero,
                        "attended_at":      attended_at,
                        "response_actions": "Entrevista con el estudiante.",
                        "sync_status":      "SYNCED",
                        "sync_version":     1,
                    },
                )
                if created:
                    count += 1
        self.stdout.write(f"  [OK] Alertas tempranas: {count}")

    def _create_risk_data_for_sy(self, enrollments, periods, failing_students, medium_risk_students):
        from apps.analytics.student_risk.infrastructure.repositories import StudentFeatureSnapshotRepository, StudentRiskScoreRepository
        from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder
        from apps.analytics.tasks import calculate_academic_risk
        snap_count = 0
        score_count = 0

        for est_tag, enrollment in enrollments.items():
            for period in periods:
                if enrollment.section.school_year_id != period.school_year_id:
                    continue

                try:
                    builder = AcademicRiskFeatureBuilder(enrollment.student_id, period.id)
                    snapshot = builder.build()
                    metrics = builder.build_persistence_metrics(snapshot)

                    snap = StudentFeatureSnapshotRepository.create_snapshot(
                        student_id=enrollment.student_id,
                        academic_period_id=period.id,
                        metrics=metrics
                    )
                    snap_count += 1

                    analysis = calculate_academic_risk(snapshot, metrics)
                    risk_score = analysis["semaforo_riesgo"]["puntaje_riesgo"]
                    risk_label = analysis["semaforo_riesgo"]["nivel"]

                    StudentRiskScoreRepository.create_score(
                        student_id=enrollment.student_id,
                        academic_period_id=period.id,
                        risk_score=risk_score,
                        risk_label=risk_label,
                        model_version="seed-v2"
                    )
                    score_count += 1

                except Exception as e:
                    self.stdout.write(f"  [WARN] Error generando riesgo para {est_tag} / {period.code}: {e}")

        self.stdout.write(f"  [OK] Feature snapshots creados: {snap_count}")
        self.stdout.write(f"  [OK] Risk scores creados: {score_count}")

    def _print_summary(self, school_year, sections, periods, students, enrollments,
                       admin_users, doc_users, rep_users, est_users):
        line = "=" * 60
        self.stdout.write(self.style.SUCCESS(f"\n{line}"))
        self.stdout.write(self.style.SUCCESS("  SEED COMPLETADO – AÑO LECTIVO"))
        self.stdout.write(self.style.SUCCESS(line))
        self.stdout.write(f"  Año escolar:       {school_year.start_date} – {school_year.end_date}")
        self.stdout.write(f"  Secciones activas: {sections.count()}")
        self.stdout.write(f"  Períodos (trim.):  {len(periods)}")
        self.stdout.write(f"  Asignaturas BGU:   {len(MATERIAS_BGU)}")
        self.stdout.write(f"  Docentes:          {len(DOCENTES)}")
        self.stdout.write(f"  Estudiantes total: {len(students)}")
        self.stdout.write(f"  Matrículas año:    {len(enrollments)}")
        self.stdout.write(f"  Representantes:    {len(rep_users)}")
        self.stdout.write(self.style.SUCCESS("-" * 60))
        self.stdout.write("  CREDENCIALES DE ACCESO (Método de acceso: username)")
        self.stdout.write(self.style.SUCCESS("-" * 60))

        self.stdout.write("  Administradores:")
        for item in ADMIN_USERS:
            u = admin_users.get(item["tag"])
            username = u.username if u else "desconocido"
            self.stdout.write(f"  [{item['tag'].upper():12}] usuario: {username:15} | pw: {item['password']:20} | correo: {item['email']}")

        self.stdout.write("  Docentes:")
        for d in DOCENTES:
            u = doc_users.get(d["tag"])
            username = u.username if u else "desconocido"
            email = u.person.email if (u and u.person) else "desconocido"
            pw    = f"Doc.{d['last_names'].split()[0]}2025!"
            self.stdout.write(f"  [{d['subject_code']:8}] usuario: {username:15} | pw: {pw:20} | correo: {email}")

        self.stdout.write("")
        self.stdout.write("  Representantes:")
        for r in REPRESENTANTES:
            u = rep_users.get(r["tag"])
            username = u.username if u else "desconocido"
            email = u.person.email if (u and u.person) else "desconocido"
            pw    = f"Rep.{r['last_names'].split()[0]}2025!"
            hijos = ", ".join(r["students"])
            self.stdout.write(f"  usuario: {username:15} | pw: {pw:20} | correo: {email:30} | estudiantes: {hijos}")

        self.stdout.write("")
        self.stdout.write("  Estudiantes (Año Activo 2025-2026):")
        for e in ESTUDIANTES:
            u = est_users.get(e["tag"])
            username = u.username if u else "desconocido"
            email = u.person.email if (u and u.person) else "desconocido"
            pw       = f"Est.{e['last_names'].split()[0]}2025!"
            self.stdout.write(f"  [{e['parallel']}] usuario: {username:15} | pw: {pw:20} | correo: {email:35} | estudiante: {u.get_full_name() if u else e['names'] + ' ' + e['last_names']}")

        self.stdout.write(self.style.SUCCESS(line))
