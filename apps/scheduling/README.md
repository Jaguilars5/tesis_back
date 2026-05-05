# Módulo `scheduling` — Gestión de Horarios y Disponibilidad

Este módulo es responsable de la organización temporal del centro educativo, gestionando las franjas horarias, la disponibilidad de los docentes y la asignación de materias a aulas y horarios específicos.

Su diseño incluye validaciones automáticas para prevenir conflictos de horario (docentes o aulas ocupadas simultáneamente) y asegurar el cumplimiento de las restricciones pedagógicas.

---

## Estructura del Módulo

```
scheduling/
├── models/         # Slots de horario, franjas y disponibilidad
├── repositories/   # Detección de conflictos y consultas de horario
├── services/       # Lógica de asignación y validación
├── api/            # Serializadores y vistas dinámicas
└── tests/          # Verificación de integridad de horarios
```

---

## Modelos de Datos

### TimeSlot (Franja Horaria)
Define las franjas horarias dentro de un régimen.

| Campo | Tipo | Verbose Name |
| :--- | :--- | :--- |
| `timing_regime` | ForeignKey (Timing_Regime) | Régimen de Horario |
| `name` | CharField (50) | Nombre |
| `day_of_week` | IntegerField | Día de la Semana |
| `start_time` | TimeField | Hora de Inicio |
| `end_time` | TimeField | Hora de Fin |
| `is_break` | BooleanField | Es Recreo |

---

## Capa de Servicios

### SchedulingService (Orquestador)

- `assign_slot`: Realiza la asignación de una materia a un horario y aula específicos. Verifica de forma atómica que el docente no tenga otro compromiso a esa hora, que el aula esté libre y que el docente haya marcado esa franja como disponible.
- `get_section_schedule`: Recupera la matriz completa de horarios para una sección (grado/paralelo) en un año escolar determinado.
- `deactivate_slot`: Desactiva un bloque de horario asignado (borrado lógico), liberando la franja horaria y el aula para nuevas asignaciones.

---

## Endpoints

Todos los endpoints son RESTful con ViewSets de DRF.

### ScheduleSlot

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/scheduling/schedule-slots/` | Listar horarios | scheduling.view_schedule |
| POST | `/api/scheduling/schedule-slots/` | Crear horario | scheduling.create_schedule |
| GET | `/api/scheduling/schedule-slots/{id}/` | Detalle | scheduling.view_schedule |
| PATCH | `/api/scheduling/schedule-slots/{id}/` | Actualizar | scheduling.update_schedule |
| DELETE | `/api/scheduling/schedule-slots/{id}/` | Eliminar | scheduling.delete_schedule |

### TimeSlot

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/scheduling/time-slots/` | Listar bloques | scheduling.view_timeslot |
| POST | `/api/scheduling/time-slots/` | Crear bloque | scheduling.create_timeslot |
| GET | `/api/scheduling/time-slots/{id}/` | Detalle | scheduling.view_timeslot |
| PATCH | `/api/scheduling/time-slots/{id}/` | Actualizar | scheduling.update_timeslot |
| DELETE | `/api/scheduling/time-slots/{id}/` | Eliminar | scheduling.delete_timeslot |

### TeacherAvailability

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/scheduling/teacher-availability/` | Listar disponibilidad | scheduling.view_availability |
| POST | `/api/scheduling/teacher-availability/` | Crear disponibilidad | scheduling.create_availability |
| GET | `/api/scheduling/teacher-availability/{id}/` | Detalle | scheduling.view_availability |
| PATCH | `/api/scheduling/teacher-availability/{id}/` | Actualizar | scheduling.update_availability |
| DELETE | `/api/scheduling/teacher-availability/{id}/` | Eliminar | scheduling.delete_availability |

### SubjectConstraint

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/scheduling/subject-constraints/` | Listar restricciones | scheduling.view_constraint |
| POST | `/api/scheduling/subject-constraints/` | Crear restricción | scheduling.create_constraint |
| GET | `/api/scheduling/subject-constraints/{id}/` | Detalle | scheduling.view_constraint |
| PATCH | `/api/scheduling/subject-constraints/{id}/` | Actualizar | scheduling.update_constraint |
| DELETE | `/api/scheduling/subject-constraints/{id}/` | Eliminar | scheduling.delete_constraint |

### ScheduleTemplateConfig

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/scheduling/schedule-configs/` | Listar plantillas | scheduling.view_template |
| POST | `/api/scheduling/schedule-configs/` | Crear plantilla | scheduling.create_template |
| GET | `/api/scheduling/schedule-configs/{id}/` | Detalle | scheduling.view_template |
| PATCH | `/api/scheduling/schedule-configs/{id}/` | Actualizar | scheduling.update_template |
| DELETE | `/api/scheduling/schedule-configs/{id}/` | Eliminar | scheduling.delete_template |

---

## Seguridad

### Autenticación y Permisos

Todos los endpoints requieren:
1. Header `Authorization: Bearer <token>`
2. Permiso específico del usuario

Permisos requeridos:

| Modelo | View | Create | Update | Delete |
|--------|------|--------|--------|--------|
| ScheduleSlot | `scheduling.view_schedule` | `scheduling.create_schedule` | `scheduling.update_schedule` | `scheduling.delete_schedule` |
| TimeSlot | `scheduling.view_timeslot` | `scheduling.create_timeslot` | `scheduling.update_timeslot` | `scheduling.delete_timeslot` |
| TeacherAvailability | `scheduling.view_availability` | `scheduling.create_availability` | `scheduling.update_availability` | `scheduling.delete_availability` |
| SubjectConstraint | `scheduling.view_constraint` | `scheduling.create_constraint` | `scheduling.update_constraint` | `scheduling.delete_constraint` |
| ScheduleTemplateConfig | `scheduling.view_template` | `scheduling.create_template` | `scheduling.update_template` | `scheduling.delete_template` |

Seedear permisos:
```bash
python manage.py seed_permissions --module scheduling
```

---

## Pruebas

```
python manage.py test apps.scheduling
```

---

## Lógica de Validación de Conflictos

1.  **Conflicto de Docente**: Un docente no puede estar asignado a dos `ScheduleSlot` diferentes en la misma franja horaria (`TimeSlot`).
2.  **Conflicto de Aula**: Un aula física no puede albergar dos clases diferentes simultáneamente.
3.  **Disponibilidad**: El sistema verifica que el docente tenga marcada la franja como "disponible" en `TeacherAvailability` antes de permitir la asignación.
