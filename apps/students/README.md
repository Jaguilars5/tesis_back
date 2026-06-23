# Módulo `students` — Gestión de Estudiantes y Matrículas

> Centraliza la información académica de los estudiantes, relaciones con representantes legales y el ciclo de vida de matrícula.

## Modelos (8)

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `Student` | Estudiante vinculado a datos personales | `person` (OneToOne, nullable), `student_code` (unique), `residential_zone` (FK), `distance_to_school_km`, `has_special_needs`, `special_needs_type` (FK), `is_active`. Hereda `TimeStampedModel` |
| `Enrollment` | Matrícula por año escolar | `student` (FK), `section` (FK), `school_year` (FK), `enrollment_status` (CharField con choices: ACT/RET/TRS/SUS/GRA), `enrollment_date`, `withdrawal_date`, `withdrawal_reason` (FK), `is_repeat`, `repeated_school_year` (FK), `created_by`, `approved_by`. Unique: `(student, section, school_year)`. Hereda `TimeStampedModel` + `SyncableModel` |
| `StudentRepresentative` | Relación estudiante-representante | `student` (FK), `person` (FK), `kinship` (FK), `is_primary`, `can_pickup`, `emergency_contact`, `receives_notifications`. Unique: `(student, person)` |
| `WithdrawalReason` | Catálogo de motivos de retiro | `code` (unique), `name` |
| `ResidentialZone` | Catálogo de zonas residenciales | `code` (unique), `name` |
| `SpecialNeedsType` | Catálogo de tipos de NEE | `code` (unique), `name` |
| `Kinship` | Catálogo de parentescos | `code` (unique), `name` |
| `EnrollmentHistory` | Historial de cambios de estado de matrícula | `enrollment` (FK), `previous_status`, `new_status`, `changed_by` (FK), `change_reason`, `effective_date` |

> **Nota:** `EnrollmentStatus` **no existe como modelo**. Es `EnrollmentStatusChoices` (TextChoices) dentro de `enrollment.py`.

## Repositorios (3)

| Repositorio | Métodos adicionales |
|-------------|---------------------|
| `StudentRepository` | `get_by_dni()`, `get_by_section()`, `search()` |
| `StudentRepresentativeRepository` | `get_by_student()`, `get_by_person()`, `get_relationship()` |
| `EnrollmentRepository` | `get_active_by_student()`, `get_by_section()`, `get_by_school_year()`, `get_students_by_section()`, `count_active_in_section()`, `has_active_enrollment()` |

## Servicios (2)

| Servicio | Métodos principales |
|----------|---------------------|
| `StudentService` | `create_student()` (crea Person + Student), `update_student()`, `deactivate_student()`, `assign_representative()`, `remove_representative()`, `set_primary_representative()`, `search_students()`, `list_students_by_section()` |
| `EnrollmentService` | `enroll_student()`, `withdraw_student()`, `transfer_student()` |

## API — Endpoints

| Método | Endpoint | ViewSet |
|--------|----------|---------|
| GET/POST | `/api/students/student/` | StudentViewSet |
| GET/PUT/PATCH/DEL | `/api/students/student/{id}/` | StudentViewSet |
| GET | `/api/students/student/search/?q=` | StudentViewSet |
| GET | `/api/students/student/by-section/?section_id=` | StudentViewSet |
| GET | `/api/students/student/{id}/representatives/` | StudentViewSet |
| GET/POST | `/api/students/enrollments/` | EnrollmentViewSet |
| GET/PUT/PATCH/DEL | `/api/students/enrollments/{id}/` | EnrollmentViewSet |
| POST | `/api/students/enrollments/{id}/withdraw/` | EnrollmentViewSet |
| POST | `/api/students/enrollments/{id}/transfer/` | EnrollmentViewSet |
| GET | `/api/students/enrollments/by-section/` | EnrollmentViewSet |
| GET | `/api/students/enrollments/by-student/` | EnrollmentViewSet |
| GET/POST | `/api/students/student-representative/` | StudentRepresentativeViewSet |
| GET/PUT/PATCH/DEL | `/api/students/student-representative/{id}/` | StudentRepresentativeViewSet |
| POST | `/api/students/student-representative/set_primary/` | StudentRepresentativeViewSet |
| DEL | `/api/students/student-representative/{id}/unlink/` | StudentRepresentativeViewSet |

> **Nota:** No existe endpoint `enrollment-statuses/`. `EnrollmentStatusChoices` es interno del modelo `Enrollment`.

## Serializers — Campos ReadOnly

| Serializer | ReadOnly |
|------------|----------|
| `StudentSerializer` | `full_name`, `age`, `id`, `created_at` |
| `StudentDetailSerializer` | hereda + `representatives` (anidado) |
| `StudentRepresentativeSerializer` | `student_names`, `person_names`, `id`, `created_at` |
| `EnrollmentSerializer` | `student_name`, `section_name`, `status_name`, `id`, `created_at`, `updated_at` |
| `EnrollmentCreateSerializer` | `enrollment_status`, `id` |

## Tests

```bash
python manage.py test apps.students --settings=config.settings.test
```

## Sincronización

`Enrollment` hereda de `SyncableModel`. Handler: `EnrollmentSyncHandler` para `source_table="enrollment"`.
