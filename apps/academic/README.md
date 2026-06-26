# Módulo `academic` — Gestión de Infraestructura Académica

> Núcleo de gestión de materias, períodos académicos, configuraciones curriculares, ofertas de materias, horarios, y asignación docente.

## Arquitectura

Cada subdominio sigue DDD (Domain-Driven Design) con 4 capas:

```
sub-app/
├── api/views.py              # ViewSet (DRF)
├── api/filters.py            # django-filter FilterSet
├── application/serializers.py # DRF ModelSerializer
├── application/validators.py # Reglas de validación puras + run_all_validators
├── domain/services.py        # Lógica de negocio (orquesta repositorio + validadores)
├── domain/repositories.py    # Interfaz (ABC)
├── infrastructure/models.py  # Django Model
├── infrastructure/repositories.py  # Implementación concreta del repositorio
├── permissions.py            # ACTION_PERMISSIONS dict
├── urls.py                   # AcademicRouter.register()
└── tests/test_api.py         # Pruebas del subdominio
```

7 sub-apps registradas en `apps.academic.__init__.py` como `ACADEMIC_APPS`.

## Modelos (7)

| Modelo | Sub-app | app_label | Campos clave |
|--------|---------|-----------|-------------|
| `Subject` | `subject/` | `academic_subject` | `name`, `code` (unique), `is_active` |
| `PeriodType` | `period_type/` | `academic_period_type` | `code` (unique), `name`, `description`, `divisions_per_year`, `is_active`. Ordenado por `name` |
| `AcademicPeriod` | `academic_period/` | `academic_period` | `school_year` (FK), `period_type` (FK PeriodType, PROTECT), `name`, `code`, `start_date`, `end_date`, `year_weight` (nullable Decimal), `is_regular_period`, `is_active`. **No tiene** `parent_period` |
| `SubjectAcademicConfig` | `subject_academic_config/` | `academic_subject_config` | `subject` (FK), `academic_grade` (FK), `weekly_hours`, `is_required`, `is_active`. Unique: `(subject, academic_grade)`. **No tiene** `pedagogical_order` |
| `SubjectOffering` | `subject_offering/` | `academic_subject_offering` | `section` (FK), `subject_academic_config` (FK), `is_active`. Unique: `(section, subject_academic_config)`. `school_year` es propiedad derivada de `section.school_year` |
| `TeacherSubjectSection` | `teacher_subject_section/` | `academic_teacher_subject` | `user` (FK), `subject_offering` (FK), `is_active`. Unique: `(user, subject_offering)`. Index: `(user, is_active)` |
| `ClassSchedule` | `class_schedule/` | `academic_class_schedule` | `teacher_subject_section` (FK), `day_of_week` (IntegerChoices 1-7), `start_time`, `end_time`, `is_active`. Unique: `(teacher_subject_section, day_of_week, start_time)`. `DayOfWeekChoices` como IntegerChoices |

> **Nota:** `AcademicPeriod` ya no tiene `parent_period`. `SubjectAcademicConfig` ya no tiene `pedagogical_order`. `SubjectOffering` ya no tiene FK directo a `school_year`.

## Repositorios (7)

Cada sub-app implementa `domain/repositories.py` (interfaz ABC) e `infrastructure/repositories.py` (implementación concreta).

| Sub-app | Repositorio | Métodos principales |
|---------|-------------|---------------------|
| `subject/` | `SubjectRepository` | `get_all()`, `get_by_id()`, `find_by_code()` |
| `period_type/` | `PeriodTypeRepository` | `get_all(active_only=True)`, `find_by_code()`, `get_or_create()` |
| `academic_period/` | `AcademicPeriodRepository` | `get_all()`, `get_by_school_year()`, `filter_by_period_type()` |
| `subject_academic_config/` | `SubjectAcademicConfigRepository` | `get_all()`, `get_by_subject()`, `get_by_grade()` |
| `subject_offering/` | `SubjectOfferingRepository` | `get_all()`, `get_by_section()`, `get_by_config()` |
| `teacher_subject_section/` | `TeacherSubjectSectionRepository` | `get_all()`, `get_by_user()`, `get_by_offering()`, `exists_by_user_and_offering()` |
| `class_schedule/` | `ClassScheduleRepository` | `get_all()`, `get_by_teacher()`, `get_by_section()`, `get_by_student()`, `get_today_for_teacher()`, `check_overlap()` |

## Servicios (7)

Cada sub-app tiene `domain/services.py` con un service class propio.

| Sub-app | Servicio | Métodos principales |
|---------|----------|---------------------|
| `subject/` | `SubjectService` | `create_subject()`, `update_subject()`, `soft_delete()` |
| `period_type/` | `PeriodTypeService` | `create_period_type()`, `update_period_type()`, `soft_delete()` |
| `academic_period/` | `AcademicPeriodService` | `create_academic_period()`, `update_academic_period()`, `soft_delete()` |
| `subject_academic_config/` | `SubjectAcademicConfigService` | `create_config()`, `update_config()`, `soft_delete()` |
| `subject_offering/` | `SubjectOfferingService` | `create_offering()`, `update_offering()`, `soft_delete()` |
| `teacher_subject_section/` | `TeacherSubjectSectionService` | `assign_teacher()`, `update_assignment()`, `soft_delete()` |
| `class_schedule/` | `ClassScheduleService` | `create_schedule()`, `update_schedule()`, `soft_delete()` |

## API — Endpoints Registrados

Todos los endpoints usan `BaseAcademicViewSet` (hereda `SoftDestroyMixin`) con `AcademicRouter`.

| Método | Endpoint (plural) | ViewSet |
|--------|-------------------|---------|
| GET/POST | `/api/academic/subjects/` | SubjectViewSet |
| GET/PUT/PATCH/DEL | `/api/academic/subjects/{id}/` | SubjectViewSet |
| POST | `/api/academic/subjects/{id}/soft-delete/` | SubjectViewSet |
| GET/POST | `/api/academic/academic-periods/` | AcademicPeriodViewSet |
| GET/PUT/PATCH/DEL | `/api/academic/academic-periods/{id}/` | AcademicPeriodViewSet |
| POST | `/api/academic/academic-periods/{id}/soft-delete/` | AcademicPeriodViewSet |
| GET/POST | `/api/academic/period-types/` | PeriodTypeViewSet |
| GET/PUT/PATCH/DEL | `/api/academic/period-types/{id}/` | PeriodTypeViewSet |
| POST | `/api/academic/period-types/{id}/soft-delete/` | PeriodTypeViewSet |
| GET/POST | `/api/academic/subject-academic-configs/` | SubjectAcademicConfigViewSet |
| GET/PUT/PATCH/DEL | `/api/academic/subject-academic-configs/{id}/` | SubjectAcademicConfigViewSet |
| POST | `/api/academic/subject-academic-configs/{id}/soft-delete/` | SubjectAcademicConfigViewSet |
| GET/POST | `/api/academic/subject-offerings/` | SubjectOfferingViewSet |
| GET/PUT/PATCH/DEL | `/api/academic/subject-offerings/{id}/` | SubjectOfferingViewSet |
| POST | `/api/academic/subject-offerings/{id}/soft-delete/` | SubjectOfferingViewSet |
| GET/POST | `/api/academic/teacher-subject-sections/` | TeacherSubjectSectionViewSet |
| GET/PUT/PATCH/DEL | `/api/academic/teacher-subject-sections/{id}/` | TeacherSubjectSectionViewSet |
| POST | `/api/academic/teacher-subject-sections/{id}/soft-delete/` | TeacherSubjectSectionViewSet |
| GET/POST | `/api/academic/class-schedules/` | ClassScheduleViewSet |
| GET/PUT/PATCH/DEL | `/api/academic/class-schedules/{id}/` | ClassScheduleViewSet |
| POST | `/api/academic/class-schedules/{id}/soft-delete/` | ClassScheduleViewSet |
| GET | `/api/academic/class-schedules/by-section/?section_id=X` | ClassScheduleViewSet |
| GET | `/api/academic/class-schedules/my-schedule/` | ClassScheduleViewSet |
| GET | `/api/academic/class-schedules/my-today/` | ClassScheduleViewSet |

> **Nota importante:** Los endpoints usan **plural** (`subjects/`, `academic-periods/`, `teacher-subject-sections/`, `class-schedules/`).

## Permisos por ViewSet

| ViewSet | Permisos usados (desde `apps.core.constants.permissions.academic`) |
|---------|--------------------------------------------------------------------|
| `SubjectViewSet` | `VIEW_SUBJECT`, `CREATE_SUBJECT`, `UPDATE_SUBJECT`, `DELETE_SUBJECT` |
| `AcademicPeriodViewSet` | `VIEW_PERIOD`, `CREATE_PERIOD`, `UPDATE_PERIOD`, `DELETE_PERIOD` |
| `PeriodTypeViewSet` | `VIEW_PERIOD_TYPE`, `CREATE_PERIOD_TYPE`, `UPDATE_PERIOD_TYPE`, `DELETE_PERIOD_TYPE` |
| `SubjectAcademicConfigViewSet` | `VIEW_SUBJECT_CONFIG`, `CREATE_SUBJECT_CONFIG`, `UPDATE_SUBJECT_CONFIG`, `DELETE_SUBJECT_CONFIG` |
| `SubjectOfferingViewSet` | `VIEW_SUBJECT_OFFERING`, `CREATE_SUBJECT_OFFERING`, `UPDATE_SUBJECT_OFFERING`, `DELETE_SUBJECT_OFFERING` |
| `TeacherSubjectSectionViewSet` | `VIEW_TEACHER_SUBJECT`, `CREATE_TEACHER_SUBJECT`, `UPDATE_TEACHER_SUBJECT`, `DELETE_TEACHER_SUBJECT` |
| `ClassScheduleViewSet` | `VIEW_CLASS_SCHEDULE`, `CREATE_CLASS_SCHEDULE`, `UPDATE_CLASS_SCHEDULE`, `DELETE_CLASS_SCHEDULE` |

## Serializers — Campos ReadOnly

| Serializer | ReadOnly |
|------------|----------|
| `SubjectSerializer` | `id`, `created_at`, `updated_at` |
| `AcademicPeriodSerializer` | `id`, `created_at`, `updated_at`, `school_year_name`, `period_type_name` |
| `PeriodTypeSerializer` | `id`, `created_at`, `updated_at` |
| `TeacherSubjectSectionSerializer` | `id`, `created_at`, `updated_at`, `user_name`, `subject_offering_name`, `subject_offering_school_year`, `subject_offering_school_year_name`, `subject_offering_section`, `subject_offering_section_name`, `subject_offering_academic_grade`, `subject_offering_academic_grade_name`, `subject_offering_subject`, `subject_offering_subject_name`, `subject_offering_config`, `subject_offering_config_name` |
| `SubjectAcademicConfigSerializer` | `id`, `created_at`, `updated_at`, `subject_name`, `academic_grade_name` |
| `SubjectOfferingSerializer` | `id`, `created_at`, `updated_at`, `school_year`, `school_year_name`, `section_name`, `subject_academic_config_name` |
| `ClassScheduleSerializer` | `id`, `created_at`, `updated_at`, `subject_offering_name`, `day_of_week_name`, `section_name`, `section_id`, `subject_name`, `subject_id`, `teacher_name`, `teacher_id` |

## Soft Delete con Confirmación

`POST /{id}/soft-delete/` requiere body `{"confirm": true}`. Integra validación en cascada:
- No permite desactivar un `Subject` con configuraciones activas asociadas
- No permite desactivar un `AcademicPeriod` con períodos hijos activos
- No permite desactivar un `TeacherSubjectSection` con horarios activos
- Etc.

## Tests

```bash
# Ejecutar tests de todos los subdominios
python manage.py test apps.academic --settings=config.settings.test

# Por sub-app
python manage.py test apps.academic.subject.tests --settings=config.settings.test
python manage.py test apps.academic.academic_period.tests --settings=config.settings.test
python manage.py test apps.academic.period_type.tests --settings=config.settings.test
python manage.py test apps.academic.subject_academic_config.tests --settings=config.settings.test
python manage.py test apps.academic.subject_offering.tests --settings=config.settings.test
python manage.py test apps.academic.teacher_subject_section.tests --settings=config.settings.test
python manage.py test apps.academic.class_schedule.tests --settings=config.settings.test
```

Total: 55+ tests distribuidos en 7 archivos `test_api.py`, 2 `test_models.py`, 1 `test_repositories.py`.

## Dependencias

- `institutions` → `SchoolYear`, `Section`, `AcademicGrade`
- `institutions_school_year`, `institutions_section`, `institutions_academic_grade` (app_labels)
- `iam` → `User`

## Índices y Unique Constraints

| Modelo | Constraints |
|--------|-------------|
| `Subject` | `code` unique |
| `PeriodType` | `code` unique |
| `AcademicPeriod` | — |
| `SubjectAcademicConfig` | Unique: `(subject, academic_grade)` |
| `SubjectOffering` | Unique: `(section, subject_academic_config)` |
| `TeacherSubjectSection` | Unique: `(user, subject_offering)`; Index: `(user, is_active)` |
| `ClassSchedule` | Unique: `(teacher_subject_section, day_of_week, start_time)` |

## Componentes Compartidos

| Archivo | Propósito |
|---------|-----------|
| `api/base.py` | `BaseAcademicViewSet`: reemplaza `retrieve` por `get`, incluye `SoftDestroyMixin` |
| `api/routers.py` | `AcademicRouter`: custom `DefaultRouter` con mappings explícitos |
| `api/urls.py` | Agrega todos los `urls.py` de cada sub-app |
| `__init__.py` | `ACADEMIC_APPS` list (para incluir en `INSTALLED_APPS`) |
