# Módulo `students` — Gestión de Estudiantes y Matrículas

> Centraliza la información académica de los estudiantes, relaciones con representantes legales y el ciclo de vida de matrícula (inscripción, transferencia, retiro).

## Modelos (9)

| Modelo | Descripción | Campos clave |
|--------|-------------|-------------|
| `Student` | Estudiante vinculado a datos personales | `person` (OneToOne a Person), `student_code` (unique), `residential_zone` (FK), `distance_to_school_km`, `has_special_needs`, `special_needs_type` (FK), `is_active`, `created_at`, `updated_at` |
| `Enrollment` | Matrícula única por año escolar | `student` (FK), `section` (FK), `school_year` (FK), `enrollment_status` (FK), `enrollment_date`, `withdrawal_date`, `withdrawal_reason` (FK a WithdrawalReason), `is_repeat`, `repeated_school_year` (FK), `created_by`, `approved_by`. Hereda `SyncableModel`. Unique: `(student, section, school_year)` |
| `EnrollmentStatus` | Catálogo de estados de matrícula | `code` (unique: ACT, RET, TRS, SUS, GRA), `name`, `is_active` |
| `StudentRepresentative` | Relación estudiante-representante | `student` (FK), `person` (FK), `kinship` (FK a Kinship), `is_primary`, `can_pickup`, `emergency_contact`, `receives_notifications`, `is_active`. Unique: `(student, person)` |
| `WithdrawalReason` | Catálogo de motivos de retiro | `code` (CAMBIO_DOMICILIO, TRASLADO, SALUD, OTRO), `name` |
| `ResidentialZone` | Catálogo de zonas residenciales | `code` (URBANA, RURAL, PERIFERICA), `name` |
| `SpecialNeedsType` | Catálogo de tipos de NEE | `code` (DISCAPACIDAD_FISICA, TDAH, AUTISMO, OTRO), `name` |
| `Kinship` | Catálogo de parentescos | `code` (PADRE, MADRE, TIO, TUTOR, OTRO), `name` |
| `EnrollmentHistory` | Historial de cambios de estado de matrícula | `enrollment` (FK), `previous_status` (FK), `new_status` (FK), `changed_by` (FK), `change_reason`, `effective_date` |

## Servicios

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `StudentService` | `create_student(document_number, names, last_names, birth_date, email, phone)` | Crea Person + Student con código único `EST-XXXXX` |
| `StudentService` | `update_student()`, `deactivate_student()` | Actualización y borrado lógico |
| `StudentService` | `assign_representative()`, `remove_representative()` | Gestión de representantes |
| `StudentService` | `set_primary_representative()`, `search_students()` | Representante principal y búsqueda |
| `EnrollmentService` | `enroll_student(student, section)` | Matricula con validación de capacidad y unicidad |
| `EnrollmentService` | `withdraw_student(enrollment, reason)` | Retiro con motivo (acepta FK o string) |
| `EnrollmentService` | `transfer_student(enrollment, new_section)` | Transferencia de sección |

## API

| Método | Endpoint | ViewSet | Permiso requerido |
|--------|----------|---------|-------------------|
| GET/POST | `/api/students/student/` | StudentViewSet | `students.view/create_student` |
| GET/PATCH/DEL | `/api/students/student/{id}/` | StudentViewSet | `students.view/update/delete_student` |
| GET | `/api/students/student/search/?q=` | StudentViewSet | `students.view_student` |
| GET | `/api/students/student/{id}/representatives/` | StudentViewSet | `students.view_relationship` |
| GET/POST | `/api/students/enrollments/` | EnrollmentViewSet | `students.view/create_enrollment` |
| GET/PATCH/DEL | `/api/students/enrollments/{id}/` | EnrollmentViewSet | `students.view/update/delete_enrollment` |
| POST | `/api/students/enrollments/{id}/withdraw/` | EnrollmentViewSet | `students.withdraw_student` |
| POST | `/api/students/enrollments/{id}/transfer/` | EnrollmentViewSet | `students.transfer_student` |
| GET | `/api/students/enrollments/by-section/?section_id=&status=` | EnrollmentViewSet | `students.view_enrollment` |
| GET | `/api/students/enrollments/by-student/?student_id=` | EnrollmentViewSet | `students.view_enrollment` |
| GET/POST | `/api/students/student-representative/` | StudentRepresentativeViewSet | `students.view/create_relationship` |
| GET/PATCH/DEL | `/api/students/student-representative/{id}/` | StudentRepresentativeViewSet | `students.view/update/delete_relationship` |
| POST | `/api/students/student-representative/set_primary/` | StudentRepresentativeViewSet | `students.update_relationship` |
| POST | `/api/students/student-representative/{id}/unlink/` | StudentRepresentativeViewSet | `students.delete_relationship` |
| GET | `/api/students/enrollment-statuses/` | EnrollmentStatusViewSet | `students.view_enrollment_status` |

## Tests

```bash
python manage.py test apps.students --settings=config.settings.test
```

## Sincronización

`Enrollment` hereda de `SyncableModel`. Handler registrado: `EnrollmentSyncHandler` para `source_table="enrollment"`.
