# Módulo `institutions` — Gestión de Base Institucional

Base estructural del sistema: años lectivos, niveles académicos, subniveles, grados y secciones.

## Modelos (5)

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `SchoolYear` | Año lectivo | `name`, `start_date`, `end_date`, `period_type` (FK, nullable), `is_active`. Hereda `TimeStampedModel` |
| `AcademicLevel` | Nivel de enseñanza | `code` (`CharField(50)`, blank, db_index), `name`, `is_active`. Ordenado por `name`. Hereda `TimeStampedModel` |
| `AcademicSublevel` | Subdivisión pedagógica dentro de un nivel | `academic_level` (FK), `code` (unique), `name`, `description`, `is_active`. Ordenado por `name`. Hereda `TimeStampedModel` |
| `AcademicGrade` | Grado dentro de un subnivel | `code` (`CharField(50)`, blank, db_index), `academic_sublevel` (FK, nullable), `name`, `sequence_order`, `is_active`. Ordenado por `sequence_order`. Propiedad `academic_level`. Hereda `TimeStampedModel` |
| `Section` | Aula/paralelo | `code` (`CharField(50)`, blank, db_index), `school_year` (FK), `academic_grade` (FK, nullable), `parallel`, `capacity`, `is_active`. Unique: `(school_year, academic_grade, parallel)`. Hereda `TimeStampedModel` |

## Repositorios (5 en 2 archivos)

| Archivo | Repositorios |
|---------|-------------|
| `institution_repo.py` | `SchoolYearRepository` (con `get_current()`, `has_overlap()`), `AcademicLevelRepository`, `AcademicSublevelRepository`, `AcademicGradeRepository` |
| `section_repository.py` | `SectionRepository` (con `get_by_school_year()`, `get_by_grade()`) |

Todos heredan de `BaseRepository` y soportan búsqueda por `?search=`.

## Servicios

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `InstitutionService` | `create_school_year()`, `get_school_year()`, `list_school_years()`, `get_current_school_year()`, `update_school_year()`, `deactivate_school_year()` | Validación de solapamiento de fechas, coherencia inicio/fin, ciclo actual |

## API — Endpoints

| Método | Endpoint | ViewSet | Permiso |
|--------|----------|---------|---------|
| GET/POST | `/api/institutions/school-year/` | SchoolYearViewSet | `institutions.view/create_school_year` |
| GET/PUT/PATCH/DEL | `/api/institutions/school-year/{id}/` | SchoolYearViewSet | `institutions.view/update/delete_school_year` |
| GET/POST | `/api/institutions/academic-levels/` | AcademicLevelViewSet | `institutions.view/create_academic_level` |
| GET/PUT/PATCH/DEL | `/api/institutions/academic-levels/{id}/` | AcademicLevelViewSet | `institutions.view/update/delete_academic_level` |
| GET/POST | `/api/institutions/academic-sublevel/` | AcademicSublevelViewSet | `institutions.view/create_academic_sublevel` |
| GET/PUT/PATCH/DEL | `/api/institutions/academic-sublevel/{id}/` | AcademicSublevelViewSet | `institutions.view/update/delete_academic_sublevel` |
| GET/POST | `/api/institutions/academic-grades/` | AcademicGradeViewSet | `institutions.view/create_academic_grade` |
| GET/PUT/PATCH/DEL | `/api/institutions/academic-grades/{id}/` | AcademicGradeViewSet | `institutions.view/update/delete_academic_grade` |
| GET/POST | `/api/institutions/section/` | SectionViewSet | `institutions.view/create_section` |
| GET/PUT/PATCH/DEL | `/api/institutions/section/{id}/` | SectionViewSet | `institutions.view/update/delete_section` |
| POST | `/api/institutions/section/{id}/soft-delete/` | SectionViewSet | `institutions.delete_section` |

> **SchoolYear `DELETE`** hace borrado lógico (`is_active=False`) vía `InstitutionService`, no elimina físicamente.

## Serializers — Campos ReadOnly

| Serializer | ReadOnly |
|------------|----------|
| `SchoolYearSerializer` | — |
| `SectionSerializer` | `school_year_name`, `academic_grade_name` |
| `AcademicLevelSerializer` | — |
| `AcademicSublevelSerializer` | `academic_level_name` |
| `AcademicGradeSerializer` | `academic_level_name` |

## Tests

```bash
python manage.py test apps.institutions --settings=config.settings.test
```

Archivos (6): `test_models.py`, `test_repositories.py`, `test_services.py`, `test_api.py`, `test_api_gaps.py`, `test_api_permissions.py`
