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

## API REST (Resumen)

El módulo utiliza el patrón de acciones basadas en POST para todas sus operaciones.

### Slots de Horario
- POST `/api/scheduling/schedule-slot/list/`
- POST `/api/scheduling/schedule-slot/get/`
- POST `/api/scheduling/schedule-slot/add/`
- POST `/api/scheduling/schedule-slot/update/`
- POST `/api/scheduling/schedule-slot/delete/`

---

## Seguridad

Header requerido:

```
Authorization: Bearer <token>
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
