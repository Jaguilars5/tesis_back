# Módulo `academic` — Gestión de Infraestructura Académica

> Núcleo de gestión de materias, períodos académicos, configuraciones curriculares, ofertas de materias, horarios, y asignación docente.

## Modelos (7)

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `Subject` | Catálogo de asignaturas | `name`, `code` (unique), `is_active` |
| `AcademicPeriod` | Períodos académicos dentro de un año lectivo | `school_year` (FK), `name`, `period_type` (FK), `parent_period` (FK self), `start_date`, `end_date`, `peso_en_anio`, `is_regular_period`, `is_active`, `code` |
| `PeriodType` | Catálogo de tipo de período | `code` (unique), `name`, `description`, `divisions_per_year` (PositiveSmallIntegerField, ej. 3 para Trimestre), `is_active`. Ordenado por `name` |
| `SubjectAcademicConfig` | Configuración curricular de materia por grado | `subject` (FK), `academic_grade` (FK), `weekly_hours`, `pedagogical_order`, `is_required`, `is_active`. Unique: `(subject, academic_grade)` |
| `SubjectOffering` | Oferta concreta de materia en una sección + año | `school_year` (FK), `section` (FK), `subject_academic_config` (FK), `is_active`. Unique: `(school_year, section, subject_academic_config)` |
| `TeacherSubjectSection` | Asignación de docente a una oferta | `user` (FK), `subject_offering` (FK), `is_active`. Unique: `(user, subject_offering)` |
| `ClassSchedule` | Horario académico | `teacher_subject_section` (FK), `day_of_week` (IntegerChoices 1-7), `start_time`, `end_time`, `is_active`. Unique: `(teacher_subject_section, day_of_week, start_time)` |

> **Nota:** `InterdisciplinaryProject`, `SubjectProject` y `DayOfWeek` **no existen** como modelos. Los días de semana se manejan como `IntegerChoices` dentro de `ClassSchedule`. No hay proyectos interdisciplinarios en este módulo.

## Repositorios (7)

| Repositorio | Métodos adicionales |
|-------------|---------------------|
| `SubjectRepository` | `get_all()` ordenado por `name` |
| `AcademicPeriodRepository` | `get_all()` ordenado por `-start_date`; `get_by_school_year()` |
| `PeriodTypeRepository` | `get_all()` ordenado por `name`; `get_by_code()` |
| `TeacherSubjectSectionRepository` | `get_all()` ordenado por `-id`; `get_by_user()`, `get_by_section()`, `get_by_subject_offering()`, `get_by_subject()`, `exists_by_user_and_offering()`, `filter_by_assignments()` |
| `SubjectAcademicConfigRepository` | `get_all()` ordenado por `-id`; `get_by_subject()`, `get_by_grade()` |
| `SubjectOfferingRepository` | `get_all()` ordenado por `-id`; `get_by_section()` (filtrable por `school_year`), `get_by_school_year()` |
| `ClassScheduleRepository` | `get_all()` ordenado por `day_of_week`, `start_time`; `get_by_subject_offering()`, `get_by_teacher()`, `check_overlap()` |

## Servicios

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `AcademicService` | `create_section()`, `get_section()`, `get_all_sections()`, `get_section_details()`, `update_section()`, `list_sections_by_school_year()` | Gestión de secciones físicas (opera sobre `institutions.Section`) |
| `AcademicService` | `create_subject()`, `get_subject()`, `get_all_subjects()`, `get_subject_details()`, `update_subject()`, `list_subjects_by_section()` | Catálogo de materias |
| `AcademicService` | `create_academic_period()`, `get_academic_period()`, `list_periods_by_school_year()`, `update_academic_period()` | Gestión de períodos académicos |
| `AcademicService` | `assign_teacher()`, `get_teacher_assignment()`, `list_teacher_assignments()`, `remove_teacher_assignment()` | Asignación docente |
| `AcademicService` | `create_schedule()`, `get_schedule()`, `get_all_schedules()`, `get_schedules_by_offering()`, `get_schedules_by_teacher()`, `update_schedule()`, `delete_schedule()` | Horarios académicos |

## API — Endpoints Registrados

| Método | Endpoint | ViewSet |
|--------|----------|---------|
| GET/POST | `/api/academic/subject/` | SubjectViewSet |
| GET/PUT/PATCH/DEL | `/api/academic/subject/{id}/` | SubjectViewSet |
| POST | `/api/academic/subject/{id}/soft-delete/` | SubjectViewSet |
| GET/POST | `/api/academic/academic-period/` | AcademicPeriodViewSet |
| GET/PUT/PATCH/DEL | `/api/academic/academic-period/{id}/` | AcademicPeriodViewSet |
| POST | `/api/academic/academic-period/{id}/soft-delete/` | AcademicPeriodViewSet |
| GET/POST | `/api/academic/teacher-subject-section/` | TeacherSubjectSectionViewSet |
| GET/PUT/PATCH/DEL | `/api/academic/teacher-subject-section/{id}/` | TeacherSubjectSectionViewSet |
| POST | `/api/academic/teacher-subject-section/{id}/soft-delete/` | TeacherSubjectSectionViewSet |
| GET/POST | `/api/academic/subject-academic-configs/` | SubjectAcademicConfigViewSet |
| GET/PUT/PATCH/DEL | `/api/academic/subject-academic-configs/{id}/` | SubjectAcademicConfigViewSet |
| POST | `/api/academic/subject-academic-configs/{id}/soft-delete/` | SubjectAcademicConfigViewSet |
| GET/POST | `/api/academic/subject-offerings/` | SubjectOfferingViewSet |
| GET/PUT/PATCH/DEL | `/api/academic/subject-offerings/{id}/` | SubjectOfferingViewSet |
| POST | `/api/academic/subject-offerings/{id}/soft-delete/` | SubjectOfferingViewSet |
| GET/POST | `/api/academic/period-types/` | PeriodTypeViewSet |
| GET/PUT/PATCH/DEL | `/api/academic/period-types/{id}/` | PeriodTypeViewSet |
| POST | `/api/academic/period-types/{id}/soft-delete/` | PeriodTypeViewSet |
| GET/POST | `/api/academic/class-schedule/` | ClassScheduleViewSet |
| GET/PUT/PATCH/DEL | `/api/academic/class-schedule/{id}/` | ClassScheduleViewSet |
| POST | `/api/academic/class-schedule/{id}/soft-delete/` | ClassScheduleViewSet |

> No existen endpoints para `interdisciplinary-projects/` ni `subject-projects/`.

## Permisos por ViewSet

| ViewSet | Permisos usados |
|---------|----------------|
| `SubjectViewSet` | `academic.view_subject`, `create_subject`, `update_subject`, `delete_subject` |
| `AcademicPeriodViewSet` | `academic.view_period`, `create_period`, `update_period`, `delete_period` |
| `TeacherSubjectSectionViewSet` | `academic.view_teacher_subject`, `create_teacher_subject`, `update_teacher_subject`, `delete_teacher_subject` |
| `SubjectAcademicConfigViewSet` | `academic.view_subject_config`, `create_subject_config`, `update_subject_config`, `delete_subject_config` |
| `SubjectOfferingViewSet` | `academic.view_subject_offering`, `create_subject_offering`, `update_subject_offering`, `delete_subject_offering` |
| `PeriodTypeViewSet` | `academic.view_period_type`, `create_period_type`, `update_period_type`, `delete_period_type` |
| `ClassScheduleViewSet` | `academic.view_class_schedule`, `create_class_schedule`, `update_class_schedule`, `delete_class_schedule` |

## Serializers — Campos ReadOnly

| Serializer | ReadOnly |
|------------|----------|
| `SubjectSerializer` | — |
| `AcademicPeriodSerializer` | `school_year_name`, `period_type_name` |
| `TeacherSubjectSectionSerializer` | `user_name`, `subject_offering_name` |
| `SubjectAcademicConfigSerializer` | `subject_name`, `academic_grade_name` |
| `SubjectOfferingSerializer` | `school_year_name`, `section_name`, `subject_academic_config_name` |
| `ClassScheduleSerializer` | `subject_offering_name`, `day_of_week_name` |
| `PeriodTypeSerializer` | — |

## Tests

```bash
python manage.py test apps.academic --settings=config.settings.test
```

Archivos de test (6): `test_models.py`, `test_api.py`, `test_api_gaps.py`, `test_api_permissions.py`, `test_repositories.py`, `test_services.py`

## Dependencias

- `institutions.SchoolYear`, `institutions.Section`, `institutions.AcademicGrade`
- `iam.User`

## Índices y Unique Constraints

| Modelo | Constraints |
|--------|-------------|
| `Subject` | `code` unique |
| `PeriodType` | `code` unique |
| `SubjectAcademicConfig` | Unique: `(subject, academic_grade)` |
| `SubjectOffering` | Unique: `(school_year, section, subject_academic_config)`; Index: `(section, school_year)` |
| `TeacherSubjectSection` | Unique: `(user, subject_offering)`; Index: `(user, is_active)` |
| `ClassSchedule` | Unique: `(teacher_subject_section, day_of_week, start_time)` |
