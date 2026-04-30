# API - Módulo Students

Esta API gestiona el registro de estudiantes, sus representantes legales y las vinculaciones entre ellos.

---

## Formato de Respuesta

Todas las peticiones exitosas devuelven el esquema estandarizado:

```json
{
  "ok": true,
  "data": {},
  "msg": ""
}
```

---

## Estudiantes (`/api/students/student/`)

### Listar Estudiantes
**GET** `/api/students/student/`

Response:
```json
{
  "ok": true,
  "data": [
    {
      "id": 1,
      "dni": "1725556660",
      "names": "Carlos Andrés"
    }
  ],
  "msg": ""
}
```

### Crear Estudiante (Matriculación)
**POST** `/api/students/student/`

Request:
```json
{
  "dni": "1725556660",
  "names": "Carlos Andrés",
  "last_names": "Mendoza Paz",
  "birth_date": "2015-05-12",
  "section": 1,
  "enrollment_number": "MAT-2024-001"
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "dni": "1725556660"
  },
  "msg": ""
}
```

### Actualizar Estudiante
**PUT** `/api/students/student/{id}/`

Request:
```json
{
  "names": "Carlos Alberto"
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "names": "Carlos Alberto"
  },
  "msg": ""
}
```

### Borrado Lógico
**POST** `/api/students/student/{id}/soft-delete/`

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "active": false
  },
  "msg": ""
}
```

---

## Representantes (`/api/students/representative/`)

### Crear Representante
**POST** `/api/students/representative/`

Request:
```json
{
  "dni": "1711122233",
  "names": "Mariana",
  "last_names": "Paz",
  "phone": "0998887766",
  "email": "mariana.paz@mail.com",
  "address": "Quito, Sector Sur"
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "dni": "1711122233"
  },
  "msg": ""
}
```

---

## Vinculación Estudiante-Representante (`/api/students/student-representative/`)

### Asignar Representante
**POST** `/api/students/student-representative/`

Request:
```json
{
  "student": 1,
  "representative": 2,
  "kinship": "Madre",
  "is_primary": true,
  "can_pickup": true,
  "emergency_contact": true,
  "receives_notifications": true
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "student": 1,
    "representative": 2
  },
  "msg": ""
}
```
