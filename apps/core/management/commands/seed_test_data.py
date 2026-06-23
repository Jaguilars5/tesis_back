"""
seed_test_data.py
Management command: seed_test_data
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pobla la base de datos con datos realistas para el año lectivo 2025-2026.
Nivel creado: Primero de Bachillerato (1ro BGU), paralelos A y B.

Características:
  • Año lectivo 2025-2026 dividido en 3 trimestres
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

from apps.academic.models import (
    AcademicPeriod,
    ClassSchedule,
    PeriodType,
    Subject,
    SubjectAcademicConfig,
    SubjectOffering,
    TeacherSubjectSection,
)
from apps.analytics.models import EarlyAlert, StudentFeatureSnapshot, StudentRiskScore
from apps.attendance.models import AttendanceStatus, Attendance
from apps.behavior.models import (
    ConductIncident,
    IncidentType,
    Severity,
)
from apps.behavior.services.behavior_service import BehaviorEvaluationService
from apps.grading.models import (
    ActivityType,
    BlockComponent,
    EvaluationBlock,
    EvaluativeActivity,
    QualitativeScale,
    StudentNote,
)
from apps.grading.signals import skip_period_summary_recalc
from apps.grading.services.grade_calculation_service import GradeCalculationService
from apps.iam.models import Role, User, UserRole
from apps.institutions.models import (
    AcademicGrade,
    AcademicLevel,
    AcademicSublevel,
    SchoolYear,
    Section,
)
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
    "end_date":   date(2026, 6, 30),
    "is_active":  True,
}

# Tres trimestres del año lectivo 2025-2026
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
        "end_date":   date(2026, 3, 13),
        "weight":     Decimal("33.33"),
    },
    {
        "code":       "T3-2526",
        "name":       "Tercer Trimestre",
        "start_date": date(2026, 3, 16),
        "end_date":   date(2026, 6, 30),
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

class Command(BaseCommand):
    help = "Siembra datos realistas para el año 2025-2026 – 1ro BGU paralelos A y B"

    def handle(self, *args, **options):
        random.seed(RANDOM_SEED)  # garantizar reproducibilidad

        self._seed_catalogs()
        self._seed_permissions_and_roles()

        school_year    = self._create_school_year()
        grade_bgu1     = self._create_grade_bgu1()
        sections       = self._create_sections(school_year, grade_bgu1)
        subjects       = self._create_subjects()
        configs        = self._create_subject_configs(subjects, grade_bgu1)
        offerings      = self._create_subject_offerings(school_year, sections, configs)
        periods        = self._create_academic_periods(school_year)

        admin_users    = self._create_admin_users()
        doc_users      = self._create_docentes()
        self._assign_roles(admin_users, doc_users)

        teacher_map    = self._create_teacher_assignments(doc_users, offerings)
        self._create_class_schedules(teacher_map, sections)

        est_users      = self._create_estudiante_users()
        students       = self._create_students(est_users)
        enrollments    = self._create_enrollments(students, sections)

        rep_users      = self._create_representante_users()
        self._create_representative_relationships(rep_users, students)

        self._create_attendance(enrollments, teacher_map, periods)
        self._create_conduct_incidents(enrollments, periods)

        grading_struct = self._create_grading_structure(periods, offerings)
        self._create_evaluative_activities(teacher_map, grading_struct, periods)
        self._create_student_notes(enrollments, grading_struct, doc_users)
        self._create_behavior_evaluations(enrollments, periods, admin_users)
        self._create_early_alerts(enrollments, periods, admin_users)
        self._create_risk_data(enrollments, periods)

        self._print_summary(
            school_year, sections, periods, students, enrollments,
            admin_users, doc_users, rep_users, est_users
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers internos
    # ─────────────────────────────────────────────────────────────────────────

    def _seed_catalogs(self):
        self.stdout.write("  -> Sembrando catálogos base...")
        call_command("seed_catalogs")

    def _seed_permissions_and_roles(self):
        self.stdout.write("  -> Sembrando permisos y roles...")
        call_command("seed_permissions")

    # ── Año escolar ──────────────────────────────────────────────────────────

    def _create_school_year(self):
        sy = SCHOOL_YEAR
        obj, created = SchoolYear.objects.get_or_create(
            start_date=sy["start_date"],
            defaults={
                "end_date":   sy["end_date"],
                "is_active":  sy["is_active"],
            },
        )
        self.stdout.write(f"  [OK] Año escolar: {obj.start_date} – {obj.end_date}")
        return obj

    # ── Estructura académica ─────────────────────────────────────────────────

    def _create_grade_bgu1(self):
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
        grade, _ = AcademicGrade.objects.get_or_create(
            code="BGU_1RO",
            defaults={
                "name":              "1ro BGU",
                "academic_sublevel": sublevel,
                "is_active":         True,
            },
        )
        self.stdout.write(f"  [OK] Grado: {grade.name}")
        return grade

    def _create_sections(self, school_year, grade):
        sections = {}
        for parallel in ("A", "B"):
            code = f"BGU1_{parallel}"
            obj, _ = Section.objects.get_or_create(
                code=code,
                defaults={
                    "school_year":    school_year,
                    "academic_grade": grade,
                    "parallel":       parallel,
                    "capacity":       35,
                    "is_active":      True,
                },
            )
            sections[parallel] = obj
            self.stdout.write(f"  [OK] Sección: 1ro BGU {parallel} (cupo 35)")
        return sections

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
        self.stdout.write(f"  [OK] Configuraciones de asignatura: {len(configs)}")
        return configs

    def _create_subject_offerings(self, school_year, sections, configs):
        """Un SubjectOffering por asignatura × sección."""
        offerings = {}   # (subject_code, parallel) → SubjectOffering
        for parallel, section in sections.items():
            for code, cfg in configs.items():
                obj, _ = SubjectOffering.objects.get_or_create(
                    section=section,
                    subject_academic_config=cfg,
                    defaults={"is_active": True},
                )
                offerings[(code, parallel)] = obj
        self.stdout.write(f"  [OK] Ofertas de asignatura: {len(offerings)}")
        return offerings

    def _create_academic_periods(self, school_year):
        period_type = PeriodType.objects.get(code="TRIMESTRE")
        objs = []
        for t in TRIMESTRES:
            obj, _ = AcademicPeriod.objects.get_or_create(
                school_year=school_year,
                code=t["code"],
                defaults={
                    "name":               t["name"],
                    "start_date":         t["start_date"],
                    "end_date":           t["end_date"],
                    "period_type":        period_type,
                    "is_regular_period":  True,
                    "is_active":          True,
                    "year_weight":        t["weight"],
                },
            )
            objs.append(obj)
            self.stdout.write(f"  [OK] Período: {obj.name} ({obj.start_date} – {obj.end_date})")
        return objs

    # ── Usuarios ─────────────────────────────────────────────────────────────

    def _make_user(self, document_number, names, last_names, email, password,
                   birth_date, is_superuser=False):
        """Crea Person + User idempotentemente. Retorna el User."""
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
        """Crea usuarios para cada docente. Credenciales predecibles por apellido."""
        users = {}
        for d in DOCENTES:
            apellido_slug = d["last_names"].split()[0].lower()
            # Eliminar tildes básicas
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

    def _create_estudiante_users(self):
        """Crea usuarios para cada estudiante. Credenciales por apellido y paralelo."""
        users = {}
        for e in ESTUDIANTES:
            apellido_slug = e["last_names"].split()[0].lower()
            for a, b in [("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("ñ","n")]:
                apellido_slug = apellido_slug.replace(a, b)
            par = e["parallel"].lower()
            email    = f"est.{apellido_slug}.{par}@uetest.edu.ec"
            password = f"Est.{e['last_names'].split()[0]}2025!"
            u = self._make_user(
                document_number=e["document_number"],
                names=e["names"],
                last_names=e["last_names"],
                email=email,
                password=password,
                birth_date=e["birth_date"],
            )
            users[e["tag"]] = u
            self.stdout.write(f"  [OK] Estudiante {e['parallel']}: {email}")
        return users

    def _create_representante_users(self):
        """Crea usuarios para cada representante."""
        users = {}
        for r in REPRESENTANTES:
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
            users[r["tag"]] = u
            self.stdout.write(f"  [OK] Representante: {email}")
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

    # ── Estudiantes ──────────────────────────────────────────────────────────

    def _create_students(self, est_users):
        students = {}
        est_role = Role.objects.get(code="ESTUDIANTE")
        for e in ESTUDIANTES:
            user = est_users[e["tag"]]
            UserRole.objects.get_or_create(user=user, role=est_role)
            student, _ = Student.objects.get_or_create(
                student_code=f"BGU1-{e['document_number'][-6:]}",
                defaults={
                    "user":              user,
                    "is_active":         True,
                    "has_special_needs": False,
                },
            )
            students[e["tag"]] = student
        self.stdout.write(f"  [OK] Estudiantes creados/verificados: {len(students)}")
        return students

    def _create_enrollments(self, students, sections):
        enrollments = {}
        for e in ESTUDIANTES:
            student = students[e["tag"]]
            section = sections[e["parallel"]]
            enrollment, _ = Enrollment.objects.get_or_create(
                student=student,
                section=section,
                defaults={
                    "enrollment_status":  "ACT",
                    "is_repeat":          False,
                    "sync_status":        "SYNCED",
                    "sync_version":       1,
                    "conflict_resolved":  False,
                },
            )
            enrollments[e["tag"]] = enrollment
        self.stdout.write(f"  [OK] Matrículas: {len(enrollments)}")
        return enrollments

    # ── Representantes ───────────────────────────────────────────────────────

    def _create_representative_relationships(self, rep_users, students):
        rep_role = Role.objects.get(code="REPRESENTANTE")
        count = 0
        for r in REPRESENTANTES:
            rep_user = rep_users[r["tag"]]
            UserRole.objects.get_or_create(user=rep_user, role=rep_role)
            kinship  = Kinship.objects.get(code=r["kinship_code"])
            for idx, student_tag in enumerate(r["students"]):
                student = students[student_tag]
                _, created = StudentRepresentative.objects.get_or_create(
                    student=student,
                    user=rep_user,
                    defaults={
                        "kinship":                kinship,
                        "is_primary":             True,
                        "receives_notifications": True,
                        "is_active":              True,
                        "emergency_contact":      idx == 0,
                    },
                )
                if created:
                    count += 1
        self.stdout.write(f"  [OK] Relaciones representante-estudiante: {count}")

    # ── Docente-Materia ──────────────────────────────────────────────────────

    def _create_teacher_assignments(self, doc_users, offerings):
        """
        Crea TeacherSubjectSection: cada docente cubre su asignatura
        en AMBOS paralelos (A y B).
        Retorna: {(subject_code, parallel) → TeacherSubjectSection}
        """
        teacher_map = {}
        for d in DOCENTES:
            user = doc_users[d["tag"]]
            scode = d["subject_code"]
            for parallel in ("A", "B"):
                key = (scode, parallel)
                offering = offerings.get(key)
                if not offering:
                    continue
                tss, _ = TeacherSubjectSection.objects.get_or_create(
                    user=user,
                    subject_offering=offering,
                    defaults={"is_active": True},
                )
                teacher_map[key] = tss
        self.stdout.write(f"  [OK] Asignaciones docente-materia: {len(teacher_map)}")
        return teacher_map

    # ── Horarios ─────────────────────────────────────────────────────────────

    def _create_class_schedules(self, teacher_map, sections):
        """
        Construye ClassSchedule a partir de SCHEDULE_SLOTS.
        Cada tupla: (subject_code, parallel, day_of_week, start_time, end_time).
        El constraint del modelo es (teacher_subject_section, day_of_week, start_time),
        lo que permite al mismo docente tener múltiples entradas en el mismo día
        siempre que la hora de inicio sea diferente (bloques no solapados).
        """
        count = 0
        seen = set()  # (tss_id, day, start) para detectar duplicados en la data

        for (scode, parallel, day, start, end) in SCHEDULE_SLOTS:
            tss = teacher_map.get((scode, parallel))
            if not tss:
                self.stdout.write(
                    f"  [WARN] Sin TSS para {scode} paralelo {parallel} – slot ignorado"
                )
                continue

            slot_key = (tss.pk, day, start)
            if slot_key in seen:
                self.stdout.write(
                    f"  [WARN] Slot duplicado en datos: {scode} {parallel} día {day} {start} – ignorado"
                )
                continue
            seen.add(slot_key)

            _, created = ClassSchedule.objects.get_or_create(
                teacher_subject_section=tss,
                day_of_week=day,
                start_time=start,
                defaults={
                    "end_time":  end,
                    "is_active": True,
                },
            )
            if created:
                count += 1

        self.stdout.write(f"  [OK] Horarios creados: {count}")

    # ── Asistencia ───────────────────────────────────────────────────────────

    def _create_attendance(self, enrollments, teacher_map, periods):
        """
        Genera registros de asistencia diarios realistas para cada clase según el horario
        y rango de fechas de cada período.
        """
        status_P = AttendanceStatus.objects.get(code="P")
        status_T = AttendanceStatus.objects.get(code="T")
        status_J = AttendanceStatus.objects.get(code="J")
        status_A = AttendanceStatus.objects.get(code="A")
        pool = [status_P] * 85 + [status_T] * 7 + [status_J] * 5 + [status_A] * 3

        # Limpiar asistencias anteriores para evitar duplicados/conflictos de formato
        Attendance.objects.all().delete()

        # Buscar todos los horarios de clase
        schedules = ClassSchedule.objects.select_related("teacher_subject_section").filter(is_active=True)

        attendance_to_create = []

        for period in periods:
            start_dt = period.start_date
            # Para el tercer trimestre, limitamos hasta el 26 de junio de 2026 (fecha de simulación)
            if period.code == "T3-2526":
                end_dt = min(period.end_date, date(2026, 6, 26))
            else:
                end_dt = period.end_date

            # Agrupar las fechas del período por día de la semana (1 = Lunes, ..., 7 = Domingo)
            current_date = start_dt
            dates_by_weekday = {i: [] for i in range(1, 8)}
            while current_date <= end_dt:
                dates_by_weekday[current_date.isoweekday()].append(current_date)
                current_date += datetime.timedelta(days=1)

            for schedule in schedules:
                tss = schedule.teacher_subject_section
                scode = tss.subject_offering.subject_academic_config.subject.code
                parallel = tss.subject_offering.section.parallel

                # Filtrar estudiantes matriculados en este paralelo
                matching_enrollments = [
                    (est_tag, enrollment)
                    for est_tag, enrollment in enrollments.items()
                    if next(e["parallel"] for e in ESTUDIANTES if e["tag"] == est_tag) == parallel
                ]

                # Fechas correspondientes al día de la semana de este horario
                dates = dates_by_weekday.get(schedule.day_of_week, [])

                for date_val in dates:
                    for est_tag, enrollment in matching_enrollments:
                        status = random.choice(pool)
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
                                conflict_resolved=False,
                            )
                        )

        if attendance_to_create:
            Attendance.objects.bulk_create(attendance_to_create, batch_size=2000)

        self.stdout.write(f"  [OK] Registros de asistencia diarios creados: {len(attendance_to_create)}")

    # ── Incidentes conductuales ───────────────────────────────────────────────

    def _create_conduct_incidents(self, enrollments, periods):
        """
        Genera 3-5 incidentes por período entre estudiantes seleccionados al azar.
        Descripción y tipo son coherentes.
        """
        count = 0
        severity_leve = Severity.objects.get(code="LEVE")
        severity_mod  = Severity.objects.get(code="MODERADA")
        all_enrollments = list(enrollments.values())

        incident_data = list(INCIDENTES_DESCRIPCION.items())

        for period in periods:
            n_incidents = random.randint(3, 5)
            targets = random.sample(all_enrollments, min(n_incidents, len(all_enrollments)))
            for enrollment in targets:
                inc_type_code, descriptions = random.choice(incident_data)
                try:
                    inc_type  = IncidentType.objects.get(code=inc_type_code)
                    severity  = severity_mod if inc_type_code == "IRRESPETO" else severity_leve
                    desc      = random.choice(descriptions)
                    incident_date = period.start_date + datetime.timedelta(
                        days=random.randint(5, 20)
                    )
                    _, created = ConductIncident.objects.get_or_create(
                        enrollment=enrollment,
                        academic_period=period,
                        incident_date=incident_date,
                        incident_type=inc_type,
                        defaults={
                            "severity":          severity,
                            "description":       desc,
                            "family_notified":   random.choice([True, False]),
                            "actions_taken":     "Diálogo con el estudiante y registro en ficha disciplinaria.",
                            "sync_status":       "SYNCED",
                            "sync_version":      1,
                            "conflict_resolved": False,
                        },
                    )
                    if created:
                        count += 1
                except IncidentType.DoesNotExist:
                    pass

        self.stdout.write(f"  [OK] Incidentes conductuales: {count}")

    # ── Estructura de evaluación ──────────────────────────────────────────────

    def _create_grading_structure(self, periods, offerings):
        """
        Por cada (período, offering) crea:
          - EvaluationBlock tipo FORMATIVA
          - BlockComponent: Tareas (40%), Lecciones (30%), Talleres (30%)
        """
        result = {}
        components_meta = [
            ("Tareas",    Decimal("40.00")),
            ("Lecciones", Decimal("30.00")),
            ("Talleres",  Decimal("30.00")),
        ]
        for period in periods:
            for (scode, parallel), offering in offerings.items():
                subject_name = offering.subject_academic_config.subject.name
                block_code = f"BLK_{period.code}_{scode}_{parallel}"
                block, _ = EvaluationBlock.objects.get_or_create(
                    code=block_code,
                    defaults={
                        "academic_period":   period,
                        "subject_offering":  offering,
                        "block_type":        "FORMATIVA",
                        "name":              f"Formativa {period.name} – {subject_name} {parallel}",
                        "weight_percentage": Decimal("100.00"),
                        "is_active":         True,
                    },
                )
                comps = []
                for comp_name, weight in components_meta:
                    comp_code = f"{block_code}_{comp_name[:3].upper()}"
                    comp, _ = BlockComponent.objects.get_or_create(
                        code=comp_code,
                        defaults={
                            "evaluation_block": block,
                            "name":             comp_name,
                            "internal_weight":  weight,
                            "is_active":        True,
                        },
                    )
                    comps.append({"component": comp, "name": comp_name})
                result[(period.code, scode, parallel)] = {
                    "block":    block,
                    "period":   period,
                    "offering": offering,
                    "comps":    comps,
                    "subject":  scode,
                }
        self.stdout.write(f"  [OK] Bloques de evaluación: {len(result)}")
        return result

    def _create_evaluative_activities(self, teacher_map, grading_struct, periods):
        """
        Crea EvaluativeActivity con títulos descriptivos por asignatura y trimestre,
        usando el catálogo ACTIVIDADES_POR_TRIMESTRE.
        """
        count = 0
        period_order = [p.code for p in periods]

        for (period_code, scode, parallel), structure in grading_struct.items():
            tss = teacher_map.get((scode, parallel))
            if not tss:
                continue

            period = structure["period"]
            actividades = ACTIVIDADES_POR_TRIMESTRE.get(period_code, [])
            # Filtrar sólo las de esta asignatura
            sub_actividades = [
                (sc, comp_name, title, atype_code)
                for (sc, comp_name, title, atype_code) in actividades
                if sc == scode
            ]

            # Mapa de componentes por nombre
            comp_by_name = {c["name"]: c["component"] for c in structure["comps"]}

            due_date = period.start_date + (
                (period.end_date - period.start_date) // 2
            )

            for (_, comp_name, title, atype_code) in sub_actividades:
                component = comp_by_name.get(comp_name)
                if not component:
                    continue
                try:
                    activity_type = ActivityType.objects.get(code=atype_code)
                except ActivityType.DoesNotExist:
                    activity_type = ActivityType.objects.get(code="TAREA")

                # Ajustar weight según cuántas actividades hay en el componente
                internal_weight = Decimal("100.00")

                obj, created = EvaluativeActivity.objects.get_or_create(
                    block_component=component,
                    teacher_subject_section=tss,
                    title=title,
                    defaults={
                        "activity_type":   activity_type,
                        "max_score":       Decimal("10.00"),
                        "internal_weight": internal_weight,
                        "due_date":        due_date,
                        "is_active":       True,
                        "sync_status":     "SYNCED",
                        "sync_version":    1,
                        "conflict_resolved": False,
                    },
                )
                if created:
                    try:
                        obj.full_clean()
                    except Exception:
                        pass
                    count += 1

        self.stdout.write(f"  [OK] Actividades evaluativas: {count}")

    # ── Notas de estudiantes ──────────────────────────────────────────────────

    def _create_student_notes(self, enrollments, grading_struct, doc_users):
        """
        Asigna StudentNote por (enrollment, activity) con notas de distribución variada.
        Cada docente califica sus propias actividades.
        Docente creador determinado por asignatura.
        """
        count = 0
        docente_by_scode = {d["subject_code"]: d["tag"] for d in DOCENTES}

        # Índice: est_tag → parallel
        est_parallel = {e["tag"]: e["parallel"] for e in ESTUDIANTES}

        with skip_period_summary_recalc():
            for (period_code, scode, parallel), structure in grading_struct.items():
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
                        if est_parallel.get(est_tag) != parallel:
                            continue

                        for activity in activities:
                            nota = random.choice(_NOTA_POOL)
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
                                    "conflict_resolved":  False,
                                },
                            )
                            if created:
                                count += 1

        self.stdout.write(f"  [OK] Notas registradas: {count}")

        # Recalcular resúmenes de calificaciones
        for period in set(s["period"] for s in grading_struct.values()):
            ids = GradeCalculationService.calculate_all_for_period(period.id)
            if ids:
                self.stdout.write(
                    f"  [OK] Resúmenes recalculados – {period.name}: {len(ids)}"
                )

    # ── Evaluaciones de conducta ──────────────────────────────────────────────

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
                    self.stdout.write(
                        f"  [WARN] Conducta – {enrollment} / {period}: {e}"
                    )
        self.stdout.write(f"  [OK] Evaluaciones de conducta: {count}")

    # ── Alertas tempranas ────────────────────────────────────────────────────

    def _create_early_alerts(self, enrollments, periods, admin_users):
        """Genera alertas para 3-4 estudiantes aleatorios en cada período."""
        count = 0
        consejero   = admin_users.get("consejero")
        all_enroll  = list(enrollments.values())
        alert_types = [
            ("low_attendance",  "Porcentaje de asistencia por debajo del umbral mínimo (80%)."),
            ("failing_grades",  "Promedio acumulado inferior a 7 puntos en una o más asignaturas."),
            ("behavior_issues", "Registro de más de dos incidentes conductuales en el período."),
        ]

        for period in periods:
            targets = random.sample(all_enroll, min(4, len(all_enroll)))
            for enrollment in targets:
                alert_type, description = random.choice(alert_types)
                attended_at = datetime.datetime.combine(
                    period.end_date,
                    datetime.time(16, 0, 0),
                    tzinfo=datetime.timezone.utc,
                )
                _, created = EarlyAlert.objects.get_or_create(
                    enrollment=enrollment,
                    academic_period=period,
                    alert_type=alert_type,
                    defaults={
                        "description":      description,
                        "urgency_level":    random.choice(["low", "medium", "high"]),
                        "attended":         True,
                        "attended_by_user": consejero,
                        "attended_at":      attended_at,
                        "response_actions": "Entrevista con el estudiante y notificación al representante.",
                        "sync_status":      "SYNCED",
                        "sync_version":     1,
                        "conflict_resolved": False,
                    },
                )
                if created:
                    count += 1
        self.stdout.write(f"  [OK] Alertas tempranas: {count}")

    # ── Datos de riesgo (analytics) ───────────────────────────────────────────

    def _create_risk_data(self, enrollments, periods):
        snap_count = 0
        score_count = 0
        labels  = ["verde", "amarillo", "rojo"]
        weights = [0.60, 0.28, 0.12]

        for enrollment in enrollments.values():
            for period in periods:
                attendance   = round(random.uniform(60, 100), 2)
                formative    = round(random.uniform(50, 100), 2)
                summative    = round(random.uniform(50, 100), 2)
                failing      = random.randint(0, 3)
                tardiness    = random.randint(0, 6)
                severe       = random.randint(0, 2)

                _, created = StudentFeatureSnapshot.objects.get_or_create(
                    enrollment=enrollment,
                    academic_period=period,
                    is_current=True,
                    defaults={
                        "attendance_rate":            Decimal(str(attendance)),
                        "consecutive_absences_max":   random.randint(0, 4),
                        "tardiness_count":            tardiness,
                        "justified_absences":         random.randint(0, 3),
                        "unjustified_absences":       random.randint(0, 4),
                        "formative_avg_normalized":   Decimal(str(formative)),
                        "summative_avg_normalized":   Decimal(str(summative)),
                        "grade_trend_slope":          Decimal(str(round(random.uniform(-4, 4), 2))),
                        "failing_subjects_count":     failing,
                        "conduct_score":              Decimal(str(round(random.uniform(65, 100), 2))),
                        "severe_incidents_count":     severe,
                        "family_notified_ratio":      Decimal(str(round(random.uniform(0.5, 1.0), 2))),
                        "prev_period_avg_grade":      Decimal(str(round(random.uniform(60, 90), 2))),
                        "age_grade_gap":              random.choice([0, 0, 0, 1]),
                        "is_repeat":                  random.random() < 0.08,
                        "has_special_needs":          random.random() < 0.05,
                        # Dimensiones analíticas (Fase 4 §5 F)
                        "city":                       getattr(
                            getattr(getattr(enrollment.student, "user", None), "person", None),
                            "city", None,
                        ),
                        "special_needs_type":         enrollment.student.special_needs_type,
                        "withdrawal_reason":          enrollment.withdrawal_reason,
                        "snapshot_trigger":           "BATCH",
                    },
                )
                if created:
                    snap_count += 1

                risk_score = round(
                    min(100, max(0,
                        (100 - attendance) * 0.35
                        + (100 - formative) * 0.35
                        + failing * 6
                        + severe * 8
                    )),
                    2,
                )
                label = random.choices(labels, weights=weights, k=1)[0]
                _, created = StudentRiskScore.objects.get_or_create(
                    enrollment=enrollment,
                    academic_period=period,
                    model_version="seed-v2",
                    defaults={
                        "risk_score": Decimal(str(risk_score)),
                        "risk_label": label,
                    },
                )
                if created:
                    score_count += 1

        self.stdout.write(f"  [OK] Feature snapshots: {snap_count}")
        self.stdout.write(f"  [OK] Risk scores: {score_count}")

    # ── Resumen final ────────────────────────────────────────────────────────

    def _print_summary(self, school_year, sections, periods, students, enrollments,
                       admin_users, doc_users, rep_users, est_users):
        line = "=" * 60
        self.stdout.write(self.style.SUCCESS(f"\n{line}"))
        self.stdout.write(self.style.SUCCESS("  SEED COMPLETADO – AÑO 2025-2026"))
        self.stdout.write(self.style.SUCCESS(line))
        self.stdout.write(f"  Año escolar:       {school_year.start_date} – {school_year.end_date}")
        self.stdout.write(f"  Grado sembrado:    1ro BGU (paralelos A y B)")
        self.stdout.write(f"  Secciones:         {len(sections)}")
        self.stdout.write(f"  Períodos (trim.):  {len(periods)}")
        self.stdout.write(f"  Asignaturas:       {len(MATERIAS_BGU)}")
        self.stdout.write(f"  Docentes:          {len(DOCENTES)}")
        self.stdout.write(f"  Estudiantes:       {len(students)}")
        self.stdout.write(f"  Matrículas:        {len(enrollments)}")
        self.stdout.write(f"  Representantes:    {len(REPRESENTANTES)}")
        self.stdout.write(self.style.SUCCESS("-" * 60))
        self.stdout.write("  CREDENCIALES DE ACCESO (Método de acceso: username)")
        self.stdout.write(self.style.SUCCESS("-" * 60))

        # Admin
        self.stdout.write("  Administradores:")
        for item in ADMIN_USERS:
            u = admin_users.get(item["tag"])
            username = u.username if u else "desconocido"
            self.stdout.write(f"  [{item['tag'].upper():12}] usuario: {username:15} | pw: {item['password']:20} | correo: {item['email']}")

        # Docentes
        self.stdout.write("")
        self.stdout.write("  Docentes:")
        for d in DOCENTES:
            u = doc_users.get(d["tag"])
            username = u.username if u else "desconocido"
            apellido_slug = d["last_names"].split()[0].lower()
            for a, b in [("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("ñ","n")]:
                apellido_slug = apellido_slug.replace(a, b)
            email = f"doc.{apellido_slug}@uetest.edu.ec"
            pw    = f"Doc.{d['last_names'].split()[0]}2025!"
            self.stdout.write(f"  [{d['subject_code']:8}] usuario: {username:15} | pw: {pw:20} | correo: {email}")

        # Representantes
        self.stdout.write("")
        self.stdout.write("  Representantes:")
        for r in REPRESENTANTES:
            u = rep_users.get(r["tag"])
            username = u.username if u else "desconocido"
            apellido_slug = r["last_names"].split()[0].lower()
            for a, b in [("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("ñ","n")]:
                apellido_slug = apellido_slug.replace(a, b)
            email = f"rep.{apellido_slug}@uetest.edu.ec"
            pw    = f"Rep.{r['last_names'].split()[0]}2025!"
            hijos = ", ".join(r["students"])
            self.stdout.write(f"  usuario: {username:15} | pw: {pw:20} | correo: {email:30} | estudiantes: {hijos}")

        # Estudiantes
        self.stdout.write("")
        self.stdout.write("  Estudiantes:")
        for e in ESTUDIANTES:
            u = est_users.get(e["tag"])
            username = u.username if u else "desconocido"
            apellido_slug = e["last_names"].split()[0].lower()
            for a, b in [("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("ñ","n")]:
                apellido_slug = apellido_slug.replace(a, b)
            par = e["parallel"].lower()
            email    = f"est.{apellido_slug}.{par}@uetest.edu.ec"
            pw       = f"Est.{e['last_names'].split()[0]}2025!"
            self.stdout.write(f"  [{e['parallel']}] usuario: {username:15} | pw: {pw:20} | correo: {email:35} | estudiante: {u.get_full_name() if u else e['names'] + ' ' + e['last_names']}")

        self.stdout.write(self.style.SUCCESS(line))
