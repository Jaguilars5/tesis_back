# API — Módulo Students

Gestiona estudiantes, matrículas y representantes legales.

## Formato de Respuesta

Todas las respuestas usan `{"ok": bool, "data": ..., "msg": "..."}` via `StandardResponseRenderer`.

## Autenticación y Permisos

Header: `Authorization: Bearer <access_token>`

| Endpoint | Método | Permiso |
|---------|--------|---------|
| `student/` | GET | `students.view_student` |
| `student/` | POST | `students.create_student` |
| `student/{id}/` | GET/PUT/PATCH | `students.view/update_student` |
| `student/{id}/` | DELETE | `students.delete_student` |
| `student/search/` | GET | `students.view_student` |
| `student/by-section/` | GET | `students.view_student` |
| `student/{id}/representatives/` | GET | `students.view_relationship` |
| `enrollments/` | GET | `students.view_enrollment` |
| `enrollments/` | POST | `students.create_enrollment` |
| `enrollments/{id}/` | GET/PUT/PATCH/DEL | `students.view/update/delete_enrollment` |
| `enrollments/{id}/withdraw/` | POST | `students.withdraw_student` |
| `enrollments/{id}/transfer/` | POST | `students.transfer_student` |
| `enrollments/by-section/` | GET | `students.view_enrollment` |
| `enrollments/by-student/` | GET | `students.view_enrollment` |
| `student-representative/` | GET/POST | `students.view/create_relationship` |
| `student-representative/{id}/` | GET/PUT/PATCH/DEL | `students.view/update/delete_relationship` |
| `student-representative/set_primary/` | POST | `students.update_relationship` |
| `student-representative/{id}/unlink/` | DELETE | `students.delete_relationship` |

---

## Estudiantes (`/api/students/student/`)

### POST — Crear (vía StudentService, crea Person + Student)

Espera: `document_number`, `names`, `last_names`, `birth_date`, `email`, `phone`.

### GET — Buscar

**GET** `/api/students/student/search/?q=Juan`

### GET — Por sección

**GET** `/api/students/student/by-section/?section_id=1`

### GET — Representantes

**GET** `/api/students/student/{id}/representatives/`

---

## Matrículas (`/api/students/enrollments/`)

### POST — Crear matrícula

```json
{"student": 1, "section": 1}
```

`enrollment_status` se asigna automáticamente como ACT.

### POST — Retirar

**POST** `/api/students/enrollments/{id}/withdraw/`

```json
{"reason": "CAMBIO_DOMICILIO"}
```

`reason` acepta código (string) o ID de `WithdrawalReason`.

### POST — Transferir

**POST** `/api/students/enrollments/{id}/transfer/`

```json
{"section_id": 2}
```

### GET — Por sección

**GET** `/api/students/enrollments/by-section/?section_id=1&status=ACT`

### GET — Por estudiante

**GET** `/api/students/enrollments/by-student/?student_id=1`

---

## Representantes (`/api/students/student-representative/`)

### POST — Asignar

```json
{
  "student": 1, "person": 5, "kinship": "PADRE",
  "is_primary": true, "can_pickup": true
}
```

`kinship` acepta ID (FK) o string (código, se resuelve contra `Kinship`).

### POST — Establecer principal

**POST** `/api/students/student-representative/set_primary/`

```json
{"student": 1, "person": 5}
```

### DELETE — Desvincular

**DELETE** `/api/students/student-representative/{id}/unlink/`

---

## Notas

- No existe endpoint `/enrollment-statuses/`. `EnrollmentStatusChoices` es interno del modelo `Enrollment` (ACT/RET/TRS/SUS/GRA).
- Student DELETE realiza soft-delete (`is_active=False`).
- Enrollment DELETE elimina físicamente (no soft-delete).
