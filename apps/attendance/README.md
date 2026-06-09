# Módulo `attendance` — Gestión de Asistencia

Este módulo gestiona el registro de asistencia diaria de los estudiantes, los catálogos de estados de asistencia y tipos de ausencia.

---

## Estructura del Módulo

```
attendance/
├── models/         # Attendance, AttendanceStatus, AbsenceType
├── repositories/   # AttendanceRepository, AttendanceStatusRepository, AbsenceTypeRepository
├── services/       # AttendanceService
├── api/            # Serializers y ViewSets REST
└── tests/          # 41 tests
```

---

## Modelos de Datos

### 1. `Attendance` (Registro de Asistencia)

| Campo | Tipo | Relación |
|-------|------|----------|
| `uuid` | `UUIDField` | Identificador único universal |
| `enrollment` | `ForeignKey` | `students.Enrollment` |
| `teacher_subject_section` | `ForeignKey` | `academic.TeacherSubjectSection` |
| `academic_period` | `ForeignKey` | `academic.AcademicPeriod` |
| `attendance_status` | `ForeignKey` | `attendance.AttendanceStatus` |
| `attendance_date` | `DateField` | Fecha del registro |
| `absence_type` | `CharField` | `justified`, `unjustified`, `late`, `none` |
| `observation` | `TextField` | Notas adicionales |
| `sync_status` | `CharField` | Estado de sincronización |
| `synced_at` | `DateTimeField` | Fecha de sincronización |

### 2. `AttendanceStatus` (Estado de Asistencia)

Catálogo de estados válidos (Presente, Ausente, Tardanza, Justificado).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `code` | `CharField(10)` | Código único (ej: `P`) |
| `name` | `CharField(100)` | Nombre descriptivo |
| `tipo` | `CharField` | `POSITIVO` o `NEGATIVO` |
| `is_active` | `BooleanField` | Activo |

### 3. `AbsenceType` (Tipo de Ausencia)

Catálogo de tipos de ausencia (Justificada, Injustificada, Atraso).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `code` | `CharField(20)` | Código único |
| `name` | `CharField(100)` | Nombre descriptivo |
| `is_active` | `BooleanField` | Activo |

---

## API Endpoints y Permisos (RBAC)

| Endpoint | Métodos | Permiso |
|----------|---------|---------|
| `/api/attendance/attendances/` | GET, POST | `attendance.view_attendance`, `attendance.create_attendance` |
| `/api/attendance/attendances/{id}/` | GET, PATCH, DELETE | `attendance.view_attendance`, `attendance.update_attendance`, `attendance.delete_attendance` |
| `/api/attendance/attendance-statuses/` | GET, POST | `attendance.view_attendance_status`, `attendance.create_attendance_status` |
| `/api/attendance/attendance-statuses/{id}/` | GET, PATCH, DELETE | `attendance.view_attendance_status`, `attendance.update_attendance_status`, `attendance.delete_attendance_status` |
| `/api/attendance/absence-types/` | GET, POST | `attendance.view_absence_type`, `attendance.create_absence_type` |
| `/api/attendance/absence-types/{id}/` | GET, PATCH, DELETE | `attendance.view_absence_type`, `attendance.update_absence_type`, `attendance.delete_absence_type` |

---

## Formato de Respuestas Enriquecidas

| Serializer | Campos enriquecidos |
|------------|---------------------|
| `AttendanceSerializer` | `enrollment_name`, `teacher_subject_section_name`, `academic_period_name`, `attendance_status_name` |

---

## Suite de Pruebas

```bash
python manage.py test apps.attendance --settings=config.settings.test
```

- **Total de Pruebas**: 41 pruebas unitarias y de integración.
