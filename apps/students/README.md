# Módulo `students` — Gestión de Estudiantes y Matrículas

Este módulo centraliza la información de los estudiantes, sus representantes legales y el proceso de matriculación.

---

## Estructura del Módulo

```
students/
├── models/         # Student, Enrollment, Representative, etc.
├── repositories/   # Consultas centralizadas (ORM)
├── services/       # Lógica de negocio y validación
├── api/            # Serializadores y ViewSets
└── tests/          # Pruebas unitarias y de integración
```

---

## Modelos de Datos

### Student (Estudiante)
Información del estudiante vinculada a una persona.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `person` | OneToOneField (Person) | Persona asociada |
| `student_code` | CharField (50) | Código único del estudiante |
| `active` | BooleanField | Activo |
| `created_at` | DateTimeField | Fecha de creación |

### EnrollmentStatus (Estado de Matrícula)
Catálogo de estados de matrícula.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `code` | CharField (10) | Código único |
| `name` | CharField (100) | Nombre |

### Enrollment (Matrícula)
Vinculación de un estudiante a una sección.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `student` | ForeignKey (Student) | Estudiante |
| `section` | ForeignKey (Section) | Sección |
| `enrollment_status` | ForeignKey (EnrollmentStatus) | Estado |
| `enrollment_date` | DateField | Fecha de matrícula |
| `sync_status` | CharField (20) | Estado de sincronización |
| `synced_at` | DateTimeField | Sincronizado el |
| `created_at` | DateTimeField | Fecha de creación |
| `updated_at` | DateTimeField | Fecha de actualización |
| `deleted_at` | DateTimeField | Fecha de eliminación |
| `sync_version` | PositiveIntegerField | Versión de sincronización |
| `device_origin` | CharField (40) | Dispositivo de origen |

### Student_Representative (Relación Estudiante-Representante)
Vinculación entre estudiante y representante.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `student` | ForeignKey (Student) | Estudiante |
| `person` | ForeignKey (Person) | Persona representante |
| `kinship` | CharField (30) | Parentesco |
| `is_primary` | BooleanField | Es principal |
| `can_pickup` | BooleanField | Puede recoger |
| `emergency_contact` | BooleanField | Contacto de emergencia |
| `receives_notifications` | BooleanField | Recibe notificaciones |
| `created_at` | DateTimeField | Fecha de creación |

**Modelo Legacy** (managed=False, no usar):
- `Representative` — Será eliminado tras migración completa

---

## API REST (Resumen)

### Estudiantes
- GET/POST `/api/students/student/`
- GET/PUT/PATCH/DELETE `/api/students/student/{id}/`

### Matrículas
- GET/POST `/api/students/enrollment/`
- GET/PUT/PATCH/DELETE `/api/students/enrollment/{id}/`

### Estados de Matrícula
- GET/POST `/api/students/enrollment-status/`

### Relaciones Estudiante-Representante
- GET/POST `/api/students/student-representative/`

---

## Seguridad

Todos los endpoints requieren `Authorization: Bearer <token>` y permiso específico.

| ViewSet | View | Create | Update | Delete |
|---------|------|--------|--------|--------|
| Student | `students.view_student` | `students.create_student` | `students.update_student` | `students.delete_student` |
| Enrollment | `students.view_enrollment` | `students.create_enrollment` | `students.update_enrollment` | `students.delete_enrollment` |
| EnrollmentStatus | `students.view_enrollment_status` | `students.create_enrollment_status` | `students.update_enrollment_status` | `students.delete_enrollment_status` |
| StudentRepresentative | `students.view_relationship` | `students.create_relationship` | `students.update_relationship` | `students.delete_relationship` |

Seedear permisos:
```bash
python manage.py seed_permissions --module students
```

---

## Pruebas

```bash
python manage.py test apps.students --settings=config.settings.test
```