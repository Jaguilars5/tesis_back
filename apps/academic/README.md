# Módulo `academic` — Gestión de Infraestructura Académica

Este módulo gestiona la infraestructura académica del sistema, incluyendo períodos académicos, secciones, ofertas de materias y asignaciones de docentes.

Su diseño sigue una arquitectura desacoplada en capas (Modelos → Repositorios → Servicios → API).

---

## Estructura del Módulo

```
academic/
├── models/         # Entidades de datos
├── repositories/   # Consultas centralizadas (ORM)
├── services/       # Lógica de negocio y cálculos
├── api/            # Serializadores y ViewSets
└── tests/          # Pruebas unitarias y de integración
```

---

## Modelos de Datos

### Academic_Period (Período Académico)
Períodos dentro de un año escolar (Quimestres, parciales, etc.)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `school_year` | ForeignKey (School_Year) | Año escolar |
| `name` | CharField (80) | Nombre del período |
| `start_date` | DateField | Fecha de inicio |
| `end_date` | DateField | Fecha de fin |
| `is_regular_period` | BooleanField | Período regular |
| `active` | BooleanField | Activo |

### Timing_Regime (Régimen de Horario)
Regímenes de asistencia (Matutina, Vespertina, Nocturna).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `institution` | ForeignKey (Institution) | Institución |
| `name` | CharField (100) | Nombre del régimen |
| `description` | TextField | Descripción |
| `active` | BooleanField | Activo |

### Section (Sección)
Representa un grado y paralelo específico dentro de un año escolar.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `school_year` | ForeignKey (School_Year) | Año escolar |
| `timing_regime` | ForeignKey (Timing_Regime) | Régimen de horario |
| `academic_grade` | ForeignKey (AcademicGrade) | Grado académico |
| `parallel` | CharField (255) | Paralelo (A, B, C...) |
| `capacity` | IntegerField | Capacidad de alumnos |
| `active` | BooleanField | Activo |

### Subject (Materia)
Asignaturas disponibles en el sistema.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | CharField (255) | Nombre de la materia |
| `code` | CharField (100) | Código único |
| `active` | BooleanField | Activo |

### SubjectAcademicConfig (Configuración de Materia por Grado)
Vincula una materia a un grado académico con parámetros pedagógicos.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `subject` | ForeignKey (Subject) | Materia |
| `academic_grade` | ForeignKey (AcademicGrade) | Grado académico |
| `weekly_hours` | IntegerField | Horas semanales |
| `pedagogical_order` | IntegerField | Orden pedagógico |
| `is_required` | BooleanField | Obligatoria |
| `active` | BooleanField | Activo |

### SubjectOffering (Oferta de Materia)
Instancia de una materia en una sección para un año escolar.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `school_year` | ForeignKey (School_Year) | Año escolar |
| `section` | ForeignKey (Section) | Sección |
| `subject_academic_config` | ForeignKey (SubjectAcademicConfig) | Configuración de materia |
| `active` | BooleanField | Activo |

### Teacher_Subject_Section (Asignación Docente)
Vincula un docente a una oferta de materia.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `user` | ForeignKey (User) | Docente |
| `subject_offering` | ForeignKey (SubjectOffering) | Oferta de materia |
| `active` | BooleanField | Activo |

**Modelos Legacy** (managed=False, no usar):
- `Config_Academic` — Reemplazado por School_Year → Academic_Period
- `Academic_Activity` — Reemplazado por jerarquía EvaluationMacro → ClassAssignment

---

## API REST (Resumen)

### Períodos y Regímenes
- GET/POST `/api/academic/academic-period/`
- GET/POST `/api/academic/timing-regime/`

### Secciones y Materias
- GET/POST `/api/academic/section/`
- GET/POST `/api/academic/subject/`
- GET/POST `/api/academic/subject-offering/`
- GET/POST `/api/academic/subject-academic-config/`
- GET/POST `/api/academic/teacher-subject-section/`

---

## Seguridad

### Autenticación y Permisos

Todos los endpoints requieren:
1. Header `Authorization: Bearer <token>`
2. Permiso específico del usuario

Permisos requeridos:

| ViewSet | View | Create | Update | Delete |
|---------|------|--------|--------|--------|
| AcademicPeriod | `academic.view_period` | `academic.create_period` | `academic.update_period` | `academic.delete_period` |
| Section | `academic.view_section` | `academic.create_section` | `academic.update_section` | `academic.delete_section` |
| Subject | `academic.view_subject` | `academic.create_subject` | `academic.update_subject` | `academic.delete_subject` |
| SubjectOffering | `academic.view_subject_offering` | `academic.create_subject_offering` | `academic.update_subject_offering` | `academic.delete_subject_offering` |
| SubjectAcademicConfig | `academic.view_subject_academic_config` | `academic.create_subject_academic_config` | `academic.update_subject_academic_config` | `academic.delete_subject_academic_config` |
| TeacherSubjectSection | `academic.view_teacher_subject` | `academic.create_teacher_subject` | `academic.update_teacher_subject` | `academic.delete_teacher_subject` |
| TimingRegime | `academic.view_regime` | `academic.create_regime` | `academic.update_regime` | `academic.delete_regime` |

Seedear permisos:
```bash
python manage.py seed_permissions --module academic
```

---

## Pruebas

```bash
python manage.py test apps.academic --settings=config.settings.test
```