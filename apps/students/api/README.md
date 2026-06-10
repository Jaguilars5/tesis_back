# API - Módulo Students

Esta API gestiona estudiantes, matrículas, representantes legales y catálogos asociados.

## Formato de Respuesta

Todas las respuestas siguen el formato `{"ok": bool, "data": ..., "msg": "..."}`.
Los listados paginados devuelven `data` con `{ count, next, previous, results }`.

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|---------|--------|---------|
| `student/` | GET/POST | `students.view/create_student` |
| `student/{id}/` | GET/PATCH/DEL | `students.view/update/delete_student` |
| `student/search/` | GET | `students.view_student` |
| `student/{id}/representatives/` | GET | `students.view_relationship` |
| `enrollments/` | GET/POST | `students.view/create_enrollment` |
| `enrollments/{id}/` | GET/PATCH/DEL | `students.view/update/delete_enrollment` |
| `enrollments/{id}/withdraw/` | POST | `students.withdraw_student` |
| `enrollments/{id}/transfer/` | POST | `students.transfer_student` |
| `enrollments/by-section/` | GET | `students.view_enrollment` |
| `enrollments/by-student/` | GET | `students.view_enrollment` |
| `student-representative/` | GET/POST | `students.view/create_relationship` |
| `student-representative/{id}/` | GET/PATCH/DEL | `students.view/update/delete_relationship` |
| `student-representative/set_primary/` | POST | `students.update_relationship` |
| `student-representative/{id}/unlink/` | POST | `students.delete_relationship` |
| `enrollment-statuses/` | GET | `students.view_enrollment_status` |

---

## Estudiantes (`/api/students/student/`)

### POST — Crear

```json
{
  "person": 1,
  "student_code": "EST-00001"
}
```

### GET — Buscar

**GET** `/api/students/student/search/?q=Juan`

### GET — Representantes del estudiante

**GET** `/api/students/student/{id}/representatives/`

---

## Matrículas (`/api/students/enrollments/`)

### POST — Crear matrícula

```json
{
  "student": 1,
  "section": 1,
  "enrollment_status": 1
}
```

### POST — Retirar estudiante

**POST** `/api/students/enrollments/{id}/withdraw/`

```json
{
  "reason": 1
}
```

`reason` acepta ID de `WithdrawalReason` o string (para crear "OTRO").

### POST — Transferir

**POST** `/api/students/enrollments/{id}/transfer/`

```json
{
  "section_id": 2
}
```

### GET — Por sección

**GET** `/api/students/enrollments/by-section/?section_id=1&status=ACT`

### GET — Por estudiante

**GET** `/api/students/enrollments/by-student/?student_id=1`

---

## Representantes (`/api/students/student-representative/`)

### POST — Asignar representante

```json
{
  "student": 1,
  "person": 5,
  "kinship": 1,
  "is_primary": true,
  "can_pickup": true
}
```

`kinship` es FK a `Kinship` (PADRE, MADRE, TUTOR, etc.)

### POST — Establecer principal

**POST** `/api/students/student-representative/set_primary/`

```json
{
  "student": 1,
  "person": 5
}
```

### POST — Desvincular

**POST** `/api/students/student-representative/{id}/unlink/`

---

## Estados de Matrícula (`/api/students/enrollment-statuses/`)

```json
{"code": "ACT", "name": "Activa"}
{"code": "RET", "name": "Retirado"}
{"code": "TRS", "name": "Transferido"}
{"code": "SUS", "name": "Suspendido"}
{"code": "GRA", "name": "Graduado"}
```
