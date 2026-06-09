# Módulo `students` — Gestión de Estudiantes y Matrículas

Este módulo centraliza la información académica de los estudiantes, sus relaciones con representantes legales y el flujo completo del ciclo de vida de matrícula (inscripción, transferencia y retiro).

---

## Estructura del Módulo

El módulo sigue un patrón de diseño por capas que garantiza la separación de responsabilidades:

```
students/
├── models/             # Definiciones de Modelos (Student, Enrollment, etc.)
├── repositories/       # Capa de Acceso a Datos (ORM Queries centralizadas)
├── services/           # Reglas de Negocio, Transacciones y Validación
├── api/                # Controladores ViewSets, Serializadores y Filtros REST
└── tests/              # Pruebas Unitarias, de Integración y de Seguridad Gaps
```

---

## Modelos de Datos

El esquema real del módulo consta de los siguientes modelos y campos, sin campos ficticios de sincronización:

### 1. `Student` (Estudiante)
Representa la información académica de un estudiante, vinculada a sus datos personales básicos en `Person`.

| Campo | Tipo Django | Descripción |
| :--- | :--- | :--- |
| `id` | `AutoField` | Identificador único primario |
| `person` | `OneToOneField(Person)` | Vinculación a los datos personales (nombres, DNI, etc.) |
| `student_code` | `CharField(50)` | Código único de registro estudiantil (Ej: `EST-00001`) |
| `active` | `BooleanField` | Indica si el estudiante está activo académica e institucionalmente |
| `created_at` | `DateTimeField` | Fecha de registro inicial (auto) |

### 2. `EnrollmentStatus` (Estado de Matrícula)
Catálogo precargado de estados en los que puede encontrarse una matrícula activa o inactiva en el sistema (ej. `ACT` para Activa, `RET` para Retirado).

| Campo | Tipo Django | Descripción |
| :--- | :--- | :--- |
| `id` | `AutoField` | Identificador único primario |
| `code` | `CharField(10)` | Código único (Ej: `ACT`, `RET`) |
| `name` | `CharField(100)` | Nombre descriptivo del estado (Ej: `Activa`, `Retirado`) |

### 3. `Enrollment` (Matrícula)
Asociación transaccional única por año escolar de un estudiante con una sección y un estado determinado.

| Campo | Tipo Django | Descripción |
| :--- | :--- | :--- |
| `id` | `AutoField` | Identificador único primario |
| `student` | `ForeignKey(Student)` | Referencia al estudiante matriculado |
| `section` | `ForeignKey(Section)` | Referencia a la sección asignada |
| `school_year` | `ForeignKey(SchoolYear)` | Año escolar correspondiente a la matrícula |
| `enrollment_status` | `ForeignKey(EnrollmentStatus)` | Estado actual de la matrícula |
| `enrollment_date` | `DateField` | Fecha en la que se efectúa la matrícula |
| `withdrawal_date` | `DateField (null)` | Fecha de retiro (opcional) |
| `withdrawal_reason` | `TextField (null)` | Razón de retiro (opcional) |
| `is_repeat` | `BooleanField` | Bandera que indica si el estudiante repite el año escolar |
| `repeated_school_year` | `ForeignKey(SchoolYear)` | Año escolar repetido (opcional) |
| `created_at` | `DateTimeField` | Sello de tiempo de creación |
| `updated_at` | `DateTimeField` | Sello de tiempo de actualización |

### 4. `StudentRepresentative` (Relación Estudiante-Representante)
Modelado de la relación de parentesco, autorización de retiro de menores y recepción de notificaciones entre estudiantes e integrantes del núcleo familiar.

| Campo | Tipo Django | Descripción |
| :--- | :--- | :--- |
| `id` | `AutoField` | Identificador único primario |
| `student` | `ForeignKey(Student)` | Estudiante asociado |
| `person` | `ForeignKey(Person)` | Persona representante legal o contacto |
| `kinship` | `CharField(30)` | Parentesco o relación (Ej: `Padre`, `Madre`, `Tío`) |
| `is_primary` | `BooleanField` | Indica si es el representante principal ante el centro |
| `can_pickup` | `BooleanField` | Indica si tiene autorización para retirar al menor de la institución |
| `emergency_contact` | `BooleanField` | Indica si debe llamarse en caso de emergencia médica/académica |
| `receives_notifications` | `BooleanField` | Suscrito al envío de calificaciones y circulares |
| `created_at` | `DateTimeField` | Sello de tiempo de registro de la asociación |

---

## Firmas de Servicios y Reglas de Negocio

La lógica transaccional de control está encapsulada en la capa de servicios:

### `StudentService`
*   `create_student(document_number, names, last_names, birth_date=None, email="", phone="", document_type_id=None)`: Crea una `Person` y asocia un código único `EST-XXXXX` a un nuevo objeto `Student`.
*   `update_student(student_id, **kwargs)`: Actualiza propiedades del estudiante o de su persona vinculada.
*   `deactivate_student(student_id)`: Marca `active=False` al estudiante (Soft Delete).
*   `assign_representative(student_id, person_id, kinship="Padre", **kwargs)`: Crea la asociación relacional.
*   `remove_representative(student_id, person_id)`: Desvincula un representante del estudiante.
*   `set_primary_representative(student_id, person_id)`: Asigna a una persona como representante principal y desmarca a cualquier otro asignado previamente.
*   `search_students(query)`: Realiza búsquedas de texto completo sobre nombres, apellidos, código de estudiante y número de identificación.

### `EnrollmentService`
*   `enroll_student(student, section, enrollment_date=None)`: Valida la capacidad de la sección seleccionada, verifica que el estudiante no cuente con una matrícula activa concurrente y registra una nueva matrícula en estado `ACT` de forma atómica.
*   `withdraw_student(enrollment, reason="")`: Marca la matrícula como `RET`, registrando la justificación de retiro y la fecha actual de retiro.
*   `transfer_student(enrollment, new_section)`: Cambia la sección asignada a una matrícula activa, verificando capacidades de la sección de destino.

---

## API REST Reference

Todos los endpoints interactivos emplean el formato estandarizado global `{"ok": true, "data": ..., "msg": "..."}`.

### Estudiantes (`/api/students/student/`)
*   `GET /api/students/student/`: Retorna la lista paginada de estudiantes activos con filtros integrados de búsqueda.
*   `POST /api/students/student/`: Crea un nuevo estudiante con su persona asociada.
*   `GET /api/students/student/{id}/`: Detalle completo de un estudiante con sus representantes incluidos.
*   `PATCH /api/students/student/{id}/`: Actualización parcial de datos del estudiante.
*   `DELETE /api/students/student/{id}/`: Desactivación lógica del estudiante.
*   `GET /api/students/student/search/?q={query}`: Buscador dinámico integrado de estudiantes.
*   `GET /api/students/student/{id}/representatives/`: Lista a todos los representantes asociados a un estudiante específico.

### Matrículas (`/api/students/enrollments/`)
*   `GET /api/students/enrollments/`: Listado de matrículas con filtros de estado e identificación.
*   `POST /api/students/enrollments/`: Registra una nueva matrícula. Retorna el objeto completo con su `id` asignado.
*   `POST /api/students/enrollments/{id}/withdraw/`: Registra el retiro formal del alumno con un cuerpo JSON de tipo `{"reason": "Motivo"}`.
*   `POST /api/students/enrollments/{id}/transfer/`: Transfiere al estudiante con cuerpo JSON `{"section_id": ID_SECCION}`.
*   `GET /api/students/enrollments/by-section/?section_id={id}&status={ACT|RET}`: Retorna las matrículas correspondientes a una sección y estado opcional.
*   `GET /api/students/enrollments/by-student/?student_id={id}`: Retorna la matrícula activa vigente del estudiante.

### Representantes (`/api/students/student-representative/`)
*   `GET /api/students/student-representative/`: Lista las vinculaciones.
*   `POST /api/students/student-representative/`: Asocia a un representante con un estudiante.
*   `POST /api/students/student-representative/set_primary/`: Establece de forma única al representante principal con cuerpo `{"student": ID, "person": ID}`.
*   `DELETE /api/students/student-representative/{id}/unlink/`: Rompe la asociación física entre representante y estudiante.

### Estados de Matrícula (`/api/students/enrollment-statuses/`)
*   `GET /api/students/enrollment-statuses/`: Listado completo de solo lectura de los estados válidos registrados en el sistema.
*   `GET /api/students/enrollment-statuses/{id}/`: Detalle del estado.

---

## Seguridad y Permisos

Todos los endpoints requieren un token JWT Bearer válido y están protegidos por el control de accesos basado en roles (RBAC) definido a nivel de cada ViewSet:

| ViewSet | Acción / Ruta | Permiso Requerido |
| :--- | :--- | :--- |
| `StudentViewSet` | `list`, `retrieve`, `by_section`, `search` | `students.view_student` |
| | `create` | `students.create_student` |
| | `update`, `partial_update` | `students.update_student` |
| | `destroy` | `students.delete_student` |
| | `representatives` | `students.view_relationship` |
| `EnrollmentViewSet` | `list`, `retrieve`, `by_section`, `by_student` | `students.view_enrollment` |
| | `create` | `students.create_enrollment` |
| | `update`, `partial_update` | `students.update_enrollment` |
| | `destroy` | `students.delete_enrollment` |
| | `withdraw` | `students.withdraw_student` |
| | `transfer` | `students.transfer_student` |
| `StudentRepresentativeViewSet` | `list`, `retrieve` | `students.view_relationship` |
| | `create` | `students.create_relationship` |
| | `update`, `partial_update`, `set_primary` | `students.update_relationship` |
| | `destroy`, `unlink` | `students.delete_relationship` |
| `EnrollmentStatusViewSet` | `list`, `retrieve` | `students.view_enrollment_status` |

Seed de permisos en Base de Datos:
```bash
python manage.py seed_permissions --module students
```

---

## Pruebas de Calidad y Cobertura

Para ejecutar la suite de pruebas del módulo (incluyendo las pruebas de integración de APIs y control de accesos RBAC de test_api_gaps.py):

```bash
python manage.py test apps.students --settings=config.settings.test
```

*   **Total de Pruebas**: 85 pruebas unitarias y de integración.
*   **Resultados de la Validación**: 100% de éxito (todas las pruebas pasan de forma limpia e independiente).