# Módulo `grading` — Registro de Desempeño y Conducta

Este módulo se encarga del seguimiento integral del estudiante, gestionando sus calificaciones, registros de asistencia e incidentes de conducta.

Su diseño garantiza que las reglas de negocio, como la normalización de notas a base 10 y el cálculo de promedios ponderados, se apliquen de forma consistente mediante una capa de servicios robusta.

---

## Estructura del Módulo

```
grading/
├── models/         # Calificaciones, Asistencia, Conducta
├── repositories/   # Consultas especializadas y filtros
├── services/       # Lógica de normalización y promedios
├── api/            # Serializadores y vistas dinámicas
└── tests/          # Verificación de lógica y cálculos
```

---

## Modelos de Datos

### StudentNote (Nota de Estudiante)
Calificaciones individuales vinculadas a una actividad académica.

| Campo | Tipo | Verbose Name |
| :--- | :--- | :--- |
| `uuid` | UUIDField | UUID |
| `student` | ForeignKey (Student) | Estudiante |
| `academic_activity` | ForeignKey (Academic_Activity) | Actividad Académica |
| `academic_period` | ForeignKey (Academic_Period) | Período Académico |
| `teacher_subject_section` | ForeignKey (Teacher_Subject_Section) | Docente-Materia-Sección |
| `note_value` | DecimalField | Valor de la Nota |
| `normalized_value` | DecimalField | Valor Normalizado |
| `observation` | TextField | Observación |
| `sync_status` | CharField (20) | Estado de Sincronización |
| `synced_at` | DateTimeField | Sincronizado el |
| `active` | BooleanField | Activo |
| `created_at` | DateTimeField | Fecha de Creación |
| `updated_at` | DateTimeField | Fecha de Actualización |
| `deleted_at` | DateTimeField | Fecha de Eliminación |
| `sync_version` | PositiveIntegerField | Versión de Sincronización |
| `device_origin` | CharField (40) | Dispositivo de Origen |

---

## Capa de Servicios

### GradingService (Orquestador)

- `create_student_note`: Registra o actualiza la nota de un estudiante para una actividad. Realiza automáticamente la normalización a base 10 basándose en el valor máximo de la actividad.
- `update_student_note`: Modifica una calificación existente y recalcula el valor normalizado si el puntaje numérico ha cambiado.
- `calculate_period_average`: Obtiene el promedio simple de las notas normalizadas de un estudiante para un período y materia específicos.
- `create_attendance`: Registra el estado de asistencia de un alumno (Presente, Ausente, etc.) para una fecha y clase determinada. Si ya existe un registro para ese día, lo actualiza.
- `list_attendance`: Recupera registros de asistencia filtrados por estudiante, sección, fecha o estado.
- `create_conduct_incident`: Documenta un evento disciplinario o académico, asignando una categoría y nivel de gravedad (Leve, Moderado, Grave).
- `list_conduct_incidents`: Lista los incidentes registrados con soporte de filtros por severidad y estado de notificación familiar.
- `deactivate_student_note`: Ejecuta un borrado lógico de una calificación marcándola como inactiva en el sistema.

---

## API REST (Resumen)

El módulo utiliza el patrón de acciones basadas en POST para todas sus operaciones CRUD.

### Calificaciones
- POST `/api/grading/student-note/list/`
- POST `/api/grading/student-note/get/`
- POST `/api/grading/student-note/add/`
- POST `/api/grading/student-note/update/`
- POST `/api/grading/student-note/soft-delete/`

---

## Seguridad

Header requerido:

```
Authorization: Bearer <token>
```

---

## Pruebas

```
python manage.py test apps.grading
```

---

## Lógica de Negocio Clave

1.  **Normalización Interna**: El servicio utiliza `_normalize_note` para asegurar que todas las notas, independientemente de su base original (20, 100, etc.), se almacenen en `normalized_value` con base 10.
2.  **Sincronización**: Los registros incluyen metadatos de sincronización (`sync_status`, `device_origin`) para soportar escenarios de uso en dispositivos móviles con conexión intermitente.
