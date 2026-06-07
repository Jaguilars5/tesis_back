# Guía de Usuario y Manual Técnico

Este documento proporciona instrucciones detalladas sobre el uso y la integración con el backend del sistema de gestión académica.

---

## Protocolo de Comunicación API

El sistema implementa una interfaz RESTful con Django REST Framework.

### Requisitos de las Peticiones

1.  **Método HTTP**: Los endpoints usan métodos estándar REST (`GET`, `POST`, `PATCH`, `DELETE`).
2.  **Cuerpo de la Petición**: Los datos deben enviarse en formato JSON (`application/json`).
3.  **Encabezados de Autenticación**: Las rutas protegidas requieren un token JWT:
    ```
    Authorization: Bearer <token_de_acceso>
    ```

### Formato de Respuesta Estándar

Todos los endpoints retornan un JSON estructurado:

```json
{
  "ok": true,
  "data": {},
  "msg": ""
}
```

| Campo | Descripción |
|-------|-------------|
| `ok` | Booleano que indica éxito o fracaso |
| `data` | Datos resultantes (objeto, lista o paginación) |
| `msg` | Mensaje descriptivo o descripción del error |

### Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | Operación exitosa |
| 201 | Recurso creado |
| 400 | Error de validación o lógica de negocio |
| 401 | No autenticado |
| 403 | Sin permisos |
| 404 | Recurso no encontrado |

---

## Gestión de Sesiones

### Inicio de Sesión
**POST** `/api/accounts/login/`

Payload:
```json
{
  "email": "usuario@ejemplo.com",
  "password": "password"
}
```

Respuesta:
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "person": { "names": "Juan", "last_names": "Pérez" },
    "institution": { "id": 1, "name": "Colegio" }
  }
}
```

### Renovación de Token
**POST** `/api/accounts/refresh/`

Payload:
```json
{
  "refresh": "token_previo"
}
```

---

## Flujos de Trabajo Comunes

### Registro de Estudiantes y Matrículas

**Paso 1**: Crear persona (opcional, si no existe)
```
POST /api/accounts/users/ (con person anidado)
```

**Paso 2**: Crear estudiante
```
POST /api/students/student/
```
Payload:
```json
{
  "person": {
    "document_type": 1,
    "document_number": "1725556660",
    "names": "Carlos",
    "last_names": "Mendoza",
    "birth_date": "2015-05-12"
  },
  "student_code": "EST-2024-001"
}
```

**Paso 3**: Matricular estudiante en sección
```
POST /api/students/enrollment/
```
Payload:
```json
{
  "student": 1,
  "section": 1,
  "enrollment_status": 1
}
```

### Registro de Calificaciones

**Prerrequisito**: El docente debe tener una asignación activa:
```
POST /api/academic/teacher-subject-section/
```

**Registrar nota**:
```
POST /api/grading/student-notes/
```
Payload:
```json
{
  "enrollment": 1,
  "class_assignment": 1,
  "grade_type": 1,
  "numeric_score": 18.50,
  "teacher_observation": "Buen trabajo"
}
```

### Registro de Asistencia y Comportamiento

```
POST /api/attendance/attendance/
```
Payload:
```json
{
  "enrollment": 1,
  "teacher_subject_section": 1,
  "academic_period": 1,
  "attendance_status": 1,
  "attendance_date": "2024-05-20"
}
```

Registrar incidente conductual:
```
POST /api/attendance/conduct-incidents/
```

---

## Sincronización Offline

Los modelos `StudentNote`, `Enrollment`, `Attendance`, `ConductIncident` y `EvaluationBlock` incluyen campos para operación offline:

| Campo | Descripción |
|-------|-------------|
| `uuid` | Identificador único del registro |
| `sync_status` | Estado: `pending`, `synced`, `conflict` |
| `synced_at` | Timestamp de última sincronización |
| `sync_version` | Versión para detección de conflictos |
| `device_origin` | Dispositivo que creó el registro |

**Estrategia de reconciliación**:
1. El cliente envía `sync_version` con cada actualización
2. Si el servidor tiene versión mayor, se rechaza la actualización
3. El cliente debe obtener los datos más recientes y reintentar

---

## Solución de Problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| `401 Unauthorized` | Token expirado | Usar `refresh` para obtener nuevo token |
| `400 Bad Request` | Payload inválido | Revisar `msg` en respuesta para detalles |
| `sync_version` conflict | Versión desactualizada | Obtener datos actuales del servidor y reintentar |
| `permission denied` | Sin permisos | Verificar que el usuario tiene el rol necesario |

---

## Endpoints por Módulo

| Módulo | Endpoints principales |
|--------|----------------------|
| **accounts** | `/api/accounts/login/`, `/api/accounts/refresh/`, `/api/accounts/users/`, `/api/accounts/roles/` |
| **institutions** | `/api/institutions/school-year/`, `/api/institutions/document-type/`, `/api/institutions/academic-level/`, `/api/institutions/academic-grade/` |
| **academic** | `/api/academic/subject/`, `/api/academic/academic-period/`, `/api/academic/subject-offering/`, `/api/academic/teacher-subject-section/` |
| **students** | `/api/students/student/`, `/api/students/enrollment/`, `/api/students/student-representative/` |
| **grading** | `/api/grading/student-notes/`, `/api/grading/evaluation-blocks/`, `/api/grading/grade-types/`, `/api/grading/recovery-processes/` |
| **attendance** | `/api/attendance/attendance/`, `/api/attendance/conduct-incidents/`, `/api/attendance/behavior-evaluations/`, `/api/attendance/socioemotional-skills/` |
| **analytics** | `/api/analytics/student-risk-scores/`, `/api/analytics/feature-snapshots/`, `/api/analytics/risk-factors/`, `/api/analytics/early-alerts/` |