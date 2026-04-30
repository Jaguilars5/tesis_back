# Módulo `students` — Gestión de Estudiantes y Representantes

Este módulo centraliza la información de los estudiantes y sus representantes legales, gestionando el proceso de matriculación, vinculación familiar y autorizaciones de retiro.

Su diseño garantiza la integridad de los datos personales y facilita la comunicación con los padres mediante una gestión estructurada de contactos primarios y secundarios.

---

## Estructura del Módulo

```
students/
├── models/         # Entidades de Estudiantes y Representantes
├── repositories/   # Búsquedas por DNI y filtros de sección
├── services/       # Lógica de vinculación y validación de edad
├── api/            # Serializadores y ViewSets (DRF)
└── tests/          # Pruebas de integridad y procesos de alta
```

---

## Modelos de Datos

### Student (Estudiante)
Información básica del estudiante.

| Campo | Tipo | Verbose Name |
| :--- | :--- | :--- |
| `uuid` | UUIDField | UUID |
| `dni` | CharField (13) | Número de Documento |
| `names` | CharField (100) | Nombres |
| `last_names` | CharField (100) | Apellidos |
| `birth_date` | DateField | Fecha de Nacimiento |
| `section` | ForeignKey (Section) | Sección |
| `enrollment_number` | CharField (50) | Número de Matrícula |
| `enrollment_date` | DateField | Fecha de Matrícula |
| `active` | BooleanField | Activo |
| `sync_status` | CharField (20) | Estado de Sincronización |
| `synced_at` | DateTimeField | Sincronizado en |
| `created_at` | DateTimeField | Fecha de Creación |
| `updated_at` | DateTimeField | Fecha de Actualización |
| `deleted_at` | DateTimeField | Fecha de Eliminación |
| `sync_version` | PositiveIntegerField | Versión de Sincronización |
| `device_origin` | CharField (40) | Dispositivo de Origen |

---

## Capa de Servicios

### StudentService (Orquestador)

- `create_student`: Registra un nuevo estudiante validando que el DNI sea único y que la edad del alumno esté en el rango permitido (5-30 años).
- `get_student_details`: Proporciona el perfil completo de un estudiante, incluyendo su sección, edad calculada y la lista detallada de sus representantes.
- `update_student`: Permite actualizar la información del estudiante, validando nuevamente la unicidad del DNI si este es modificado.
- `create_representative`: Registra a un tutor o responsable legal en el sistema, asegurando la no duplicidad mediante el DNI.
- `assign_representative`: Vincula a un estudiante con un representante, definiendo su parentesco y niveles de autorización (retiro, notificaciones, etc.).
- `set_primary_representative`: Designa a un representante específico como el contacto principal del estudiante para comunicaciones oficiales.
- `get_contact_info_for_student`: Retorna de forma estructurada los números de teléfono y correos electrónicos de todos los representantes activos del estudiante.
- `remove_representative`: Desvincula a un representante de un estudiante, validando que el alumno no se quede sin al menos un responsable legal asignado.

---

## API REST (Resumen)

El módulo utiliza ViewSets estándar de Django Rest Framework.

### Estudiantes
- GET/POST `/api/students/student/`
- GET/PUT/PATCH/DELETE `/api/students/student/{id}/`
- POST `/api/students/student/{id}/soft-delete/`

---

## Seguridad

Header requerido:

```
Authorization: Bearer <token>
```

---

## Pruebas

```
python manage.py test apps.students
```

---

## Validaciones Críticas

1.  **DNI Único**: El sistema previene el registro duplicado de estudiantes o representantes mediante la validación obligatoria del DNI.
2.  **Rango de Edad**: Se valida que la fecha de nacimiento del estudiante resulte en una edad válida para el sistema escolar (ej: 5 a 30 años).
3.  **Representante Único**: No se puede eliminar el último representante vinculado a un estudiante activo para asegurar que siempre exista un contacto responsable.
