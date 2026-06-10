# Módulo `academic` — Gestión de Infraestructura Académica

> Núcleo de gestión de materias, períodos académicos, configuraciones curriculares, ofertas de materias, horarios, proyectos interdisciplinarios y asignación docente.

## Modelos (10)

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `Subject` | Catálogo de asignaturas | `name`, `code` (unique), `is_active` |
| `AcademicPeriod` | Períodos de evaluación dentro de un año lectivo | `school_year` (FK), `name`, `period_type` (FK), `parent_period` (FK self), `start_date`, `end_date`, `is_regular_period`, `is_active`, `code` |
| `PeriodType` | Catálogo de tipo de período | `code` (REGULAR, SUPLETORIO, REFUERZO), `name` |
| `SubjectAcademicConfig` | Configuración curricular de materia por grado | `subject` (FK), `academic_grade` (FK), `weekly_hours`, `pedagogical_order`, `is_required`, `is_active` |
| `SubjectOffering` | Oferta concreta de materia en una sección + año | `school_year` (FK), `section` (FK), `subject_academic_config` (FK), `is_active`. Unique: `(school_year, section, subject_academic_config)` |
| `TeacherSubjectSection` | Asignación de docente a una oferta | `user` (FK), `subject_offering` (FK), `is_active`. Unique: `(user, subject_offering)` |
| `InterdisciplinaryProject` | Proyecto que abarca múltiples asignaturas | `academic_period` (FK), `subject_offerings` (M2M via SubjectProject), `title`, `start_date`, `delivery_date`, `product_max_score`, `presentation_max_score`, `product_rubric`, `presentation_rubric`, `is_active` |
| `SubjectProject` | Tabla puente: asignatura ↔ proyecto | `interdisciplinary_project` (FK), `subject_offering` (FK), `responsible_teacher` (FK User). Unique: `(interdisciplinary_project, subject_offering)` |
| `DayOfWeek` | Catálogo de días de la semana | `code` (1-7), `name` |
| `ClassSchedule` | Horario académico | `subject_offering` (FK), `day_of_week` (FK), `start_time`, `end_time`, `classroom`, `building`, `is_active`. Unique: `(subject_offering, day_of_week, start_time)` |

## Servicios

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `AcademicService` | `create_section()`, `get_section()`, `get_section_details()`, `update_section()` | Gestión de secciones físicas |
| `AcademicService` | `create_subject()`, `get_subject_details()` | Catálogo de materias |
| `AcademicService` | `create_academic_period()` | Creación de períodos con validación de fechas |
| `AcademicService` | `assign_teacher()`, `list_teacher_assignments()`, `remove_teacher_assignment()` | Asignación docente |

## API

| Método | Endpoint | ViewSet | Permiso requerido |
|--------|----------|---------|-------------------|
| GET/POST | `/api/academic/subject/` | SubjectViewSet | `academic.view/create_subject` |
| GET/PATCH/DEL | `/api/academic/subject/{id}/` | SubjectViewSet | `academic.view/update/delete_subject` |
| POST | `/api/academic/subject/{id}/soft-delete/` | SubjectViewSet | `academic.delete_subject` |
| GET/POST | `/api/academic/academic-period/` | AcademicPeriodViewSet | `academic.view/create_period` |
| GET/PATCH/DEL | `/api/academic/academic-period/{id}/` | AcademicPeriodViewSet | `academic.view/update/delete_period` |
| POST | `/api/academic/academic-period/{id}/soft-delete/` | AcademicPeriodViewSet | `academic.delete_period` |
| GET/POST | `/api/academic/teacher-subject-section/` | TeacherSubjectSectionViewSet | `academic.view/create_teacher_subject` |
| GET/PATCH/DEL | `/api/academic/teacher-subject-section/{id}/` | TeacherSubjectSectionViewSet | `academic.view/update/delete_teacher_subject` |
| POST | `/api/academic/teacher-subject-section/{id}/soft-delete/` | TeacherSubjectSectionViewSet | `academic.delete_teacher_subject` |
| GET/POST | `/api/academic/subject-academic-configs/` | SubjectAcademicConfigViewSet | `academic.view/create_subject_config` |
| GET/PATCH/DEL | `/api/academic/subject-academic-configs/{id}/` | SubjectAcademicConfigViewSet | `academic.view/update/delete_subject_config` |
| GET/POST | `/api/academic/subject-offerings/` | SubjectOfferingViewSet | `academic.view/create_subject_offering` |
| GET/PATCH/DEL | `/api/academic/subject-offerings/{id}/` | SubjectOfferingViewSet | `academic.view/update/delete_subject_offering` |
| GET/POST | `/api/academic/interdisciplinary-projects/` | InterdisciplinaryProjectViewSet | `academic.view/create_interdisciplinary_project` |
| GET/PATCH/DEL | `/api/academic/interdisciplinary-projects/{id}/` | InterdisciplinaryProjectViewSet | `academic.view/update/delete_interdisciplinary_project` |
| GET/POST | `/api/academic/subject-projects/` | SubjectProjectViewSet | `academic.view/create_subject_project` |
| GET/PATCH/DEL | `/api/academic/subject-projects/{id}/` | SubjectProjectViewSet | `academic.view/update/delete_subject_project` |
| GET/POST | `/api/academic/period-types/` | PeriodTypeViewSet | `academic.view/create_period_type` |
| GET/PATCH/DEL | `/api/academic/period-types/{id}/` | PeriodTypeViewSet | `academic.view/update/delete_period_type` |

**Nota:** `DayOfWeek` y `ClassSchedule` existen como modelos con serializers pero **no tienen ViewSets** en la API actual.

## Respuestas Enriquecidas

| Serializer | Campos readonly |
|------------|-----------------|
| `AcademicPeriodSerializer` | `school_year_name` |
| `TeacherSubjectSectionSerializer` | `user_name`, `subject_offering_name` |
| `SubjectAcademicConfigSerializer` | `subject_name`, `academic_grade_name` |
| `SubjectOfferingSerializer` | `school_year_name`, `section_name`, `subject_academic_config_name` |
| `SubjectProjectSerializer` | `interdisciplinary_project_title`, `subject_offering_name` |
| `InterdisciplinaryProjectSerializer` | `academic_period_name`, `subject_projects` (anidado) |
| `ClassScheduleSerializer` | `subject_offering_name`, `day_of_week_name` |
| `SubjectSerializer` | — |
| `DayOfWeekSerializer` | — |
| `PeriodTypeSerializer` | — |

## Tests

```bash
python manage.py test apps.academic --settings=config.settings.test
```

## Dependencias

- `institutions.SchoolYear`, `institutions.Section`, `institutions.AcademicGrade`
- `iam.User`

## Índices

| Modelo | Índices |
|--------|---------|
| `SubjectOffering` | `(section, school_year)` |
| `TeacherSubjectSection` | `(user, is_active)` |
| `ClassSchedule` | Unique: `(subject_offering, day_of_week, start_time)` |
