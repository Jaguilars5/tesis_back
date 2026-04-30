# API - Módulo Scheduling

Esta API gestiona la organización temporal del centro: franjas horarias, disponibilidad docente y asignaciones de clases.

---

## Formato de Respuesta

Todas las peticiones devuelven el esquema estandarizado:

```json
{
  "ok": true,
  "data": {},
  "msg": ""
}
```

---

## Patrón de Endpoints

El módulo `scheduling` utiliza el patrón de acciones basadas en POST para todas las operaciones.

### Asignación de Horarios (`/api/scheduling/schedule-slot/`)

#### Listar Slots
**POST** `/api/scheduling/schedule-slot/list/`

Response:
```json
{
  "ok": true,
  "data": [
    {
      "id": 1,
      "time_slot": 5,
      "classroom": 10
    }
  ],
  "msg": ""
}
```

#### Asignar Horario (Agregar)
**POST** `/api/scheduling/schedule-slot/add/`

Request:
```json
{
  "teacher_subject_section": 1,
  "school_year": 1,
  "time_slot": 5,
  "classroom": 10,
  "is_manual": true
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "time_slot": 5
  },
  "msg": ""
}
```

#### Eliminar Asignación
**POST** `/api/scheduling/schedule-slot/delete/`

Request:
```json
{
  "id": 1
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "deleted": true
  },
  "msg": ""
}
```

---

## Disponibilidad Docente (`/api/scheduling/teacher-availability/`)

### Registrar Disponibilidad
**POST** `/api/scheduling/teacher-availability/add/`

Request:
```json
{
  "user": 5,
  "school_year": 1,
  "time_slot": 10,
  "is_available": true
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "is_available": true
  },
  "msg": ""
}
```

---

## Franjas Horarias (`/api/scheduling/time-slot/`)

### Crear Franja
**POST** `/api/scheduling/time-slot/add/`

Request:
```json
{
  "day_of_week": 1,
  "start_time": "07:00:00",
  "end_time": "07:45:00"
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "day_of_week": 1
  },
  "msg": ""
}
```
