# API - Módulo Students

Esta API gestiona el registro de estudiantes, sus matrículas y la relación con representantes legales.

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

## Autenticación y Permisos

Header requerido:
```
Authorization: Bearer <access_token>
```

| Endpoint | Método | Permiso |
|---------|--------|---------|
| `student/` | GET | `students.view_student` |
| `student/` | POST | `students.create_student` |
| `student/{id}/` | GET | `students.view_student` |
| `student/{id}/` | PATCH | `students.update_student` |
| `student/{id}/` | DELETE | `students.delete_student` |
| `enrollment/` | GET | `students.view_enrollment` |
| `enrollment/` | POST | `students.create_enrollment` |
| `student-representative/` | GET | `students.view_relationship` |
| `student-representative/` | POST | `students.create_relationship` |

---

## Estudiantes (`/api/students/student/`)

### Listar
**GET** `/api/students/student/`

Response (paginado):
```json
{
  "ok": true,
  "data": {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "student_code": "EST-2024-001",
        "person": {
          "id": 1,
          "document_number": "1725556660",
          "names": "Carlos Andrés",
          "last_names": "Mendoza Paz"
        },
        "active": true
      }
    ]
  },
  "msg": ""
}
```

### Crear Estudiante
**POST** `/api/students/student/`

Request:
```json
{
  "person": {
    "document_type": 1,
    "document_number": "1725556660",
    "names": "Carlos Andrés",
    "last_names": "Mendoza Paz",
    "birth_date": "2015-05-12",
    "email": "carlos@mail.com"
  },
  "student_code": "EST-2024-001"
}
```

### Obtener
**GET** `/api/students/student/{id}/`

### Actualizar
**PATCH** `/api/students/student/{id}/`

### Eliminar (soft delete)
**DELETE** `/api/students/student/{id}/`

---

## Matrículas (`/api/students/enrollment/`)

### Listar
**GET** `/api/students/enrollment/`

Response (paginado):
```json
{
  "ok": true,
  "data": {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "student": 1,
        "section": 1,
        "enrollment_status": 1,
        "enrollment_date": "2024-09-01"
      }
    ]
  },
  "msg": ""
}
```

### Crear Matrícula
**POST** `/api/students/enrollment/`

Request:
```json
{
  "student": 1,
  "section": 1,
  "enrollment_status": 1
}
```

### Obtener
**GET** `/api/students/enrollment/{id}/`

### Actualizar
**PATCH** `/api/students/enrollment/{id}/`

---

## Estados de Matrícula (`/api/students/enrollment-status/`)

### Listar
**GET** `/api/students/enrollment-status/`

### Crear
**POST** `/api/students/enrollment-status/`

Request:
```json
{
  "code": "ACTIVE",
  "name": "Activo"
}
```

---

## Relaciones Estudiante-Representante (`/api/students/student-representative/`)

### Listar
**GET** `/api/students/student-representative/`

### Crear
**POST** `/api/students/student-representative/`

Request:
```json
{
  "student": 1,
  "person": 5,
  "kinship": "Madre",
  "is_primary": true,
  "can_pickup": true,
  "emergency_contact": true,
  "receives_notifications": true
}
```

### Obtener
**GET** `/api/students/student-representative/{id}/`

### Actualizar
**PATCH** `/api/students/student-representative/{id}/`

### Eliminar
**DELETE** `/api/students/student-representative/{id}/`