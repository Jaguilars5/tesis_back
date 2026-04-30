# Módulo Academic

Gestión de infraestructura académica: configuraciones, períodos, secciones, asignaturas, actividades evaluativas y calificaciones de estudiantes.

## Estructura de Carpetas

```
academic/
├── models/                    # Capa de datos (8 modelos)
│   ├── __init__.py           # Re-export de modelos
│   ├── section.py            # Secciones (grados/paralelos)
│   ├── subject.py            # Asignaturas/materias
│   ├── config_academic.py    # Configuración académica
│   ├── academic_period.py    # Períodos (quimestres, parciales)
│   ├── academic_activity.py  # Tipos de evaluación
│   ├── timing_regime.py      # Regímenes horarios
│   ├── teacher_subject_section.py  # Asignaciones docentes
│   └── student_note.py       # Calificaciones
│
├── repositories/             # Capa de acceso a datos
│   ├── __init__.py
│   └── academic_repo.py      # 8 repository classes
│
├── services/                 # Capa de lógica de negocio
│   ├── __init__.py
│   └── academic_service.py   # AcademicService (40+ métodos)
│
├── api/                      # Capa HTTP (REST)
│   ├── __init__.py
│   ├── serializers.py        # Serializadores DRF
│   ├── views.py              # ViewSets
│   ├── filters.py            # Filtros
│   └── urls.py               # Router DRF
│
├── tests/                    # Tests (3 suites)
│   ├── __init__.py
│   ├── test_models.py        # Tests de modelos (10+ casos)
│   ├── test_services.py      # Tests de servicios (15+ casos)
│   └── test_api.py           # Tests HTTP (10+ casos)
│
├── admin.py                  # Panel de administración
├── apps.py                   # Configuración de app
├── urls.py                   # Rutas (includes api/urls.py)
├── README.md                 # Este archivo
└── migrations/               # Auto-generadas
```

## Arquitectura de Capas

### 1. Modelos (`models/`)

Ocho modelos que representan la infraestructura académica completa.

#### Config_Academic

- `school_year` (FK → SchoolYear)
- `institution` (FK → Institution)
- `academic_period_type` (CharField) - "Quimestral", "Trimestral", etc.
- `number_of_periods` (IntegerField) - Ej: 2 (quimestres)
- `description` (TextField)
- timestamps

#### Timing_Regime

- `school_year` (FK → SchoolYear)
- `name` (CharField) - "Matutina", "Vespertina", "Nocturna"
- `description` (TextField, opcional)

#### Section

- `school_year` (FK → SchoolYear)
- `timing_regime` (FK → Timing_Regime, nullable)
- `level` (CharField) - "Primaria", "Secundaria"
- `grade` (CharField) - "6to", "7mo", "8vo"
- `parallel` (CharField) - "A", "B", "C"
- `capacity` (IntegerField)
- timestamps

#### Subject

- `school_year` (FK → SchoolYear)
- `section` (FK → Section)
- `name` (CharField) - "Matemática", "Lenguaje"
- `code` (CharField) - "MAT-001"
- `credits` (IntegerField, default=0)
- `description` (TextField)
- timestamps

#### Academic_Period

- `config_academic` (FK → Config_Academic)
- `name` (CharField) - "Quimestre 1"
- `number` (IntegerField)
- `description` (TextField)
- timestamps

#### Academic_Activity

- `config_academic` (FK → Config_Academic)
- `subject` (FK → Subject)
- `name` (CharField) - "Examen", "Lección", "Proyecto"
- `value_max` (DecimalField) - Máximo valor (ej: 20)
- `weight` (DecimalField) - Peso en cálculo (0-1)
- `applies_to` (CharField) - "all", "approved", etc.
- `is_recoverable` (BooleanField) - Puede recuperarse
- `order` (IntegerField) - Orden de ejecución
- timestamps

#### Teacher_Subject_Section

- `user` (FK → User, docente)
- `subject` (FK → Subject)
- `section` (FK → Section)
- `school_year` (FK → SchoolYear)
- `unique_together` = ('user', 'subject', 'section', 'school_year')
- timestamps

#### Student_Note

- `student` (FK → Student)
- `academic_activity` (FK → Academic_Activity)
- `academic_period` (FK → Academic_Period)
- `teacher_subject_section` (FK → Teacher_Subject_Section)
- `note_value` (DecimalField) - Valor registrado
- `normalized_value` (DecimalField) - Valor normalizado a 10
- `observation` (TextField)
- `sync_status` (CharField) - "pending", "synced"
- `sync_timestamp` (BigIntegerField) - Timestamp de sincronización
- `sync_version` (PositiveIntegerField) - Versión para conflictos
- `device_origin` (CharField) - Dispositivo origen
- `active` (BooleanField, default=True)
- timestamps

### 2. Repositorios (`repositories/`)

Encapsulan todas las queries complejas. Heredan de `BaseRepository`.

#### 8 Repository Classes

- `SectionRepository`
- `SubjectRepository`
- `ConfigAcademicRepository`
- `AcademicPeriodRepository`
- `AcademicActivityRepository`
- `TimingRegimeRepository`
- `TeacherSubjectSectionRepository`
- `StudentNoteRepository`

Cada uno con métodos: `get_all()`, `get_by_id(pk)`

### 3. Servicios (`services/`)

`AcademicService` con 40+ métodos divididos en 8 grupos.

#### Config_Academic (4 métodos)

- `create_config_academic(school_year_id, institution_id, ...)`
- `get_config_academic(config_id)`
- `list_configs(school_year_id=None)`
- `update_config_academic(config_id, **kwargs)`

#### Timing_Regime (4 métodos)

- `create_timing_regime(school_year_id, name, description='')`
- `get_timing_regime(regime_id)`
- `list_timing_regimes(school_year_id=None)`
- `update_timing_regime(regime_id, **kwargs)`

#### Section (6 métodos)

- `create_section(school_year_id, timing_regime_id, level, grade, parallel, capacity)`
- `get_section(section_id)`
- `get_all_sections()`
- `get_section_details(section_id)` - Incluye asignaturas y docentes
- `list_sections_by_school_year(school_year_id)`
- `update_section(section_id, **kwargs)`

#### Subject (6 métodos)

- `create_subject(school_year_id, section_id, name, code, credits=0, description='')`
- `get_subject(subject_id)`
- `get_all_subjects()`
- `get_subject_details(subject_id)` - Incluye docentes y actividades
- `list_subjects_by_section(section_id)`
- `update_subject(subject_id, **kwargs)`

#### Academic_Period (4 métodos)

- `create_academic_period(config_academic_id, name, number, description='')`
- `get_academic_period(period_id)`
- `list_periods_by_config(config_id)`
- `update_academic_period(period_id, **kwargs)`

#### Academic_Activity (5 métodos)

- `create_academic_activity(config_academic_id, subject_id, name, value_max, weight, applies_to, ...)`
- `get_academic_activity(activity_id)`
- `list_activities_by_subject(subject_id)`
- `update_academic_activity(activity_id, **kwargs)`
- Validaciones: `value_max > 0`, `weight ∈ [0, 1]`

#### Teacher_Subject_Section (4 métodos)

- `assign_teacher(user_id, subject_id, section_id, school_year_id)`
- `get_teacher_assignment(assignment_id)`
- `list_teacher_assignments(user_id=None, subject_id=None, section_id=None)`
- `remove_teacher_assignment(assignment_id)`

#### Student_Note (8+ métodos)

- `record_student_note(student_id, academic_activity_id, academic_period_id, ..., note_value, ...)`
- `get_student_note(note_id)`
- `list_student_notes(student_id=None, academic_period_id=None, subject_id=None, section_id=None)`
- `calculate_period_average(student_id, subject_id, academic_period_id)` - Promedio ponderado
- `calculate_section_average(section_id, subject_id, academic_period_id)` - Promedio de grupo
- `mark_notes_synced(note_ids)` - Marca como sincronizado
- `deactivate_student_note(note_id)` - Soft-delete
- **Normalización automática**: Nota de 20 → escala 10

### 4. API (`api/`)

Endpoints REST con validación y filtrado.

**ViewSets (>10):**

- `SectionViewSet` - CRUD + filtros
- `SubjectViewSet` - CRUD + filtros
- `AcademicActivityViewSet` - CRUD
- `TimingRegimeViewSet` - CRUD
- Y más...

**Rutas registradas:**

```
/api/academic/section/              - Secciones
/api/academic/subject/              - Asignaturas
/api/academic/academic-activity/    - Actividades
/api/academic/timing-regime/        - Regímenes
/api/academic/student-note/         - Calificaciones
```

### 5. Tests (`tests/`)

#### test_models.py (10+ casos)

- Creación, validaciones, relaciones, timestamps

#### test_services.py (15+ casos)

- CRUD para cada modelo
- Validaciones (capacity > 0, peso válido, etc.)
- Cálculos de promedios
- Excepciones

#### test_api.py (10+ casos)

- Endpoints HTTP
- Filtros
- CRUD via API

## Ejemplos de Uso

### Crear estructura académica

```python
from apps.academic.services.academic_service import AcademicService

# 1. Crear configuración
config = AcademicService.create_config_academic(
    school_year_id=1,
    institution_id=1,
    academic_period_type='Quimestral',
    number_of_periods=2
)

# 2. Crear sección
section = AcademicService.create_section(
    school_year_id=1,
    timing_regime_id=1,
    level='Primaria',
    grade='6to',
    parallel='A',
    capacity=40
)

# 3. Crear asignatura
subject = AcademicService.create_subject(
    school_year_id=1,
    section_id=section.id,
    name='Matemática',
    code='MAT-001',
    credits=3
)
```

### Registrar calificación

```python
# Registra nota y calcula automáticamente valor normalizado
note = AcademicService.record_student_note(
    student_id=1,
    academic_activity_id=5,
    academic_period_id=1,
    teacher_subject_section_id=1,
    note_value=16,  # De máximo 20
    observation='Excelente desempeño'
)
# nota.normalized_value = 8.0 (16/20 * 10)
```

### Calcular promedios

```python
# Promedio del estudiante en una materia/período
average = AcademicService.calculate_period_average(
    student_id=1,
    subject_id=1,
    academic_period_id=1
)
# Calcula ponderado según weight de cada actividad

# Promedio de toda la sección
section_avg = AcademicService.calculate_section_average(
    section_id=1,
    subject_id=1,
    academic_period_id=1
)
```

### Asignar docentes

```python
assignment = AcademicService.assign_teacher(
    user_id=5,  # ID del docente
    subject_id=1,
    section_id=1,
    school_year_id=1
)
```

## Validaciones Importantes

1. **Section**: Capacidad > 0, no duplicados por (school_year, level, grade, parallel)
2. **Academic_Activity**:
   - value_max > 0
   - weight ∈ [0, 1]
3. **Student_Note**:
   - note_value ∈ [0, value_max]
   - Se normaliza automáticamente a escala 10
4. **Teacher_Subject_Section**: Único por (user, subject, section, school_year)

## Cálculos Especiales

### Normalización de Notas

```
nota_normalizada = (nota_registrada / valor_maximo) × 10

Ej: Si value_max=20 y student ingresa 15:
    normalized = (15 / 20) × 10 = 7.5
```

### Promedio Ponderado

```
promedio = Σ(nota_normalizada × peso) / Σ(pesos)

Ej:
  Examen (peso 0.5): 8.0
  Lección (peso 0.3): 7.5
  Proyecto (peso 0.2): 9.0

  promedio = (8.0×0.5 + 7.5×0.3 + 9.0×0.2) / 1.0 = 8.15
```

## Sincronización de Notas

Las calificaciones tienen control de sincronización:

- `sync_status`: 'pending' | 'synced'
- `sync_timestamp`: Timestamp de último sincronizado
- `sync_version`: Incremento para detectar conflictos
- `device_origin`: Dispositivo que registró la nota

```python
# Marcar como sincronizadas
AcademicService.mark_notes_synced([1, 2, 3])
```
