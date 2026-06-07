# 🧠 Master Prompt — Refactor Integral SIGAE

> **Propósito:** Guía ejecutable para reestructurar el backend Django alineándolo con el ERD (`docs/bd_en.html`), aplicando arquitectura en capas y principios SOLID.
>
> **Stack:** Django + DRF + PostgreSQL + Celery
> **Patrón:** Models → Repositories → Services → API (por app)
> **Estilo:** ViewSets, `StandardResponseRenderer`, `action_permissions`, `ok_response`/`error_response`

---

## 📋 Instrucciones Generales para el Agente

1. **Seguir el orden jerárquico:** Cada fase depende de la anterior. No saltar fases.
2. **Respetar la arquitectura en capas:** Models → Repositories → Services → API. Nunca poner lógica ORM en views/services.
3. **Aplicar SOLID:**
   - **S** — Cada app con una única responsabilidad (ver tabla en Fase 0)
   - **O** — Repositorios y servicios extensibles sin modificar modelos
   - **L** — Repositorios con interfaz consistente
   - **I** — ViewSets con `action_permissions` específicos
   - **D** — API depende de Services, Services depende de Repositories
4. **Convenciones:**
   - Modelos: `PascalCase` (ej: `PeriodGradeSummary`)
   - Apps: `snake_case` (ej: `attendance`)
   - FKs: `modelo = ForeignKey(App.Model, ...)` sin sufijo `_id`
   - Respuestas: `ok_response(data)` / `error_response(msg)`
   - Tests: `TestCase` + `APIClient`, NO pytest
5. **Validar cada fase:** Correr `python manage.py check` y `python manage.py test` después de cada fase.

---

## Fase 0 — Línea Base y Preparación

> **Objetivo:** Establecer el estado actual, crear estructura de apps nuevas y verificar que todo compila.

### Paso 0.1: Crear estructura de apps nuevas

Crear las siguientes apps con `python manage.py startapp`:

```bash
python manage.py startapp attendance apps/attendance
```

### Paso 0.2: Verificar instalación

Agregar `apps.attendance` a `LOCAL_APPS` en `config/settings/base.py`:

```python
LOCAL_APPS = [
    "apps.core",
    "apps.accounts",
    "apps.academic",
    "apps.grading",
    "apps.institutions",
    "apps.scheduling",
    "apps.students",
    "apps.analytics",
    "apps.attendance",  # 🆕 Nueva app
]
```

### Paso 0.3: Verificar compilación

```bash
python manage.py check --settings=config.settings.local
python manage.py makemigrations --settings=config.settings.local
```

### ✅ Criterio de éxito

- `attendance` creada con `apps.py`, `models/__init__.py`, `admin.py`, `urls.py`
- `INSTALLED_APPS` actualizado
- `python manage.py check` sin errores

---

## Fase 1 — Infraestructura y Core (SRP: capa base)

> **Objetivo:** Crear/ajustar modelos de infraestructura transversal que no dependen de otras apps.
>
> **Principios:** S (infraestructura), D (core no depende de nadie)

### Paso 1.1: Crear `SyncQueue` en `apps/core`

**Archivo:** `apps/core/models/sync_queue.py`

```python
import uuid
from django.db import models


class SyncQueue(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID")
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        verbose_name="Usuario origen",
    )
    source_table = models.CharField(max_length=100, verbose_name="Tabla origen")
    record_uuid = models.UUIDField(verbose_name="UUID del registro")
    operation = models.CharField(
        max_length=20,
        choices=[
            ("create", "Crear"),
            ("update", "Actualizar"),
            ("delete", "Eliminar"),
        ],
        verbose_name="Operación",
    )
    payload = models.JSONField(verbose_name="Payload", default=dict, blank=True)
    attempts = models.PositiveIntegerField(default=0, verbose_name="Intentos")
    last_error = models.TextField(null=True, blank=True, verbose_name="Último error")
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pendiente"),
            ("processing", "Procesando"),
            ("completed", "Completado"),
            ("failed", "Fallido"),
        ],
        default="pending",
        verbose_name="Estado",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Procesado en")

    class Meta:
        app_label = "core"
        verbose_name = "Cola de Sincronización"
        verbose_name_plural = "Colas de Sincronización"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["source_table", "record_uuid"]),
        ]

    def __str__(self):
        return f"{self.operation} - {self.source_table} ({self.status})"
```

### Paso 1.2: Exportar en `apps/core/models/__init__.py`

```python
from .system_config import SystemConfig
from .sync_queue import SyncQueue

__all__ = ["SystemConfig", "SyncQueue"]
```

### Paso 1.3: Migrar

```bash
python manage.py makemigrations core --settings=config.settings.local
python manage.py migrate core --settings=config.settings.local
```

### ✅ Criterio de éxito

- `SyncQueue` creado con todos los campos
- Migración aplicada sin errores
- `python manage.py check` ok

---

## Fase 2 — Catálogos y Estructura Institucional (SRP: instituciones)

> **Objetivo:** Mover `Section` de `academic` a `institutions` para que `institutions` gestione TODA la jerarquía estructural.
>
> **Principios:** S (institutions = estructura del centro), O (repositorios extensibles)

### Paso 2.1: Mover `Section` a `institutions`

**Crear:** `apps/institutions/models/section.py`

```python
from django.db import models


class Section(models.Model):
    school_year = models.ForeignKey(
        "institutions.School_Year",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
    )
    academic_grade = models.ForeignKey(
        "institutions.AcademicGrade",
        on_delete=models.CASCADE,
        verbose_name="Grado Académico",
        null=True,
    )
    parallel = models.CharField(max_length=255, verbose_name="Paralelo")
    capacity = models.IntegerField(verbose_name="Capacidad")
    active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "institutions"
        verbose_name = "Sección"
        verbose_name_plural = "Secciones"

    def __str__(self):
        if self.academic_grade:
            return f"{self.school_year.name} - {self.academic_grade.name} {self.parallel}"
        return f"{self.school_year.name} - {self.parallel}"
```

### Paso 2.2: Actualizar `apps/institutions/models/__init__.py`

```python
from .school_year import School_Year
from .classroom import Classroom
from .document_type import DocumentType
from .room_type import RoomType
from .academic_level import AcademicLevel
from .academic_grade import AcademicGrade
from .section import Section  # ◀️ Movido desde academic

__all__ = ["School_Year", "Classroom", "DocumentType", "RoomType", "AcademicLevel", "AcademicGrade", "Section"]
```

### Paso 2.3: Eliminar `Section` de `academic`

1. Eliminar `apps/academic/models/section.py`
2. Actualizar `apps/academic/models/__init__.py` removiendo `Section`

### Paso 2.4: Actualizar todos los FKs que apuntan a `academic.Section`

Buscar y reemplazar en TODAS las apps:

| Buscar                                     | Reemplazar                                     |
| ------------------------------------------ | ---------------------------------------------- |
| `"academic.Section"`                       | `"institutions.Section"`                       |
| `from apps.academic.models import Section` | `from apps.institutions.models import Section` |

**Apps afectadas:**

- `apps/students/models/enrollment.py` (FK a Section)
- `apps/academic/models/subject_offering.py` (FK a Section)
- `apps/scheduling/models/schedule_slot.py` (si aplica)
- Cualquier repositorio/servicio que importe `Section` desde `academic`

### Paso 2.5: Migrar

```bash
python manage.py makemigrations institutions academic --settings=config.settings.local
python manage.py migrate --settings=config.settings.local
```

### ✅ Criterio de éxito

- `Section` existe SOLO en `institutions`
- Ningún import roto a `academic.Section`
- `python manage.py check` sin errores
- Tests de `Enrollment`, `SubjectOffering` pasan

---

## Fase 3 — Personas y Seguridad (SRP: accounts)

> **Objetivo:** Verificar que `accounts` está completo y alineado con el ERD.
>
> **Principios:** S (accounts = identidad + acceso), I (permisos granulares por ViewSet)

### Paso 3.1: Verificar modelos existentes

| Modelo           | ERD         | Estado      |
| ---------------- | ----------- | ----------- |
| `Person`         | PERSONA     | ✅ Completo |
| `User`           | USUARIO     | ✅ Completo |
| `Role`           | ROL         | ✅ Completo |
| `Permission`     | PERMISO     | ✅ Completo |
| `UserRole`       | USUARIO_ROL | ✅ Completo |
| `RolePermission` | ROL_PERMISO | ✅ Completo |

### ✅ Criterio de éxito

- No se requieren cambios en `accounts`
- Tests de permisos y autenticación pasan

---

## Fase 4 — Estudiantes y Matrículas (SRP: students)

> **Objetivo:** Agregar campos faltantes a `Student` y `Enrollment` según ERD.
>
> **Principios:** S (students = perfil estudiantil + matrícula + familia)

### Paso 4.1: Agregar campos a `Student`

**Archivo:** `apps/students/models/student.py`

Agregar después de `distance_to_school_km`:

```python
    has_special_needs = models.BooleanField(
        default=False, verbose_name="Tiene NEE"
    )
    special_needs_type = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Tipo de NEE"
    )
```

### Paso 4.2: Agregar campos a `Enrollment`

**Archivo:** `apps/students/models/enrollment.py`

Agregar después de `student`:

```python
    school_year = models.ForeignKey(
        "institutions.School_Year",
        on_delete=models.CASCADE,
        verbose_name="Año Escolar",
    )
```

Agregar después de `withdrawal_reason`:

```python
    is_repeat = models.BooleanField(default=False, verbose_name="Es repitente")
    repeated_school_year = models.ForeignKey(
        "institutions.School_Year",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="repeated_enrollments",
        verbose_name="Año escolar repetido",
    )
```

### Paso 4.3: Migrar

```bash
python manage.py makemigrations students --settings=config.settings.local
python manage.py migrate students --settings=config.settings.local
```

### ✅ Criterio de éxito

- `Student` tiene `has_special_needs` y `special_needs_type`
- `Enrollment` tiene `school_year`, `is_repeat`, `repeated_school_year`
- Tests de estudiantes pasan

---

## Fase 5 — Núcleo Académico (SRP: academic)

> **Objetivo:** Agregar campo `period_type` a `Academic_Period` y crear modelos de proyectos interdisciplinarios.
>
> **Principios:** S (academic = oferta académica + periodos + proyectos), O (extensible con nuevos modelos)

### Paso 5.1: Agregar `period_type` a `Academic_Period`

**Archivo:** `apps/academic/models/academic_period.py`

Agregar después de `name`:

```python
    period_type = models.CharField(
        max_length=50,
        choices=[
            ("ordinary", "Ordinario"),
            ("recovery", "Recuperación"),
            ("intensive", "Intensivo"),
            ("special", "Especial"),
        ],
        default="ordinary",
        verbose_name="Tipo de período",
    )
```

### Paso 5.2: Crear `InterdisciplinaryProject`

**Archivo:** `apps/academic/models/interdisciplinary_project.py`

```python
from django.db import models


class InterdisciplinaryProject(models.Model):
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        related_name="interdisciplinary_projects",
        verbose_name="Período Académico",
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    start_date = models.DateField(verbose_name="Fecha de inicio")
    delivery_date = models.DateField(verbose_name="Fecha de entrega")
    active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        app_label = "academic"
        verbose_name = "Proyecto Interdisciplinario"
        verbose_name_plural = "Proyectos Interdisciplinarios"
        ordering = ["-start_date"]

    def __str__(self):
        return self.title
```

### Paso 5.3: Crear `SubjectProject`

**Archivo:** `apps/academic/models/subject_project.py`

```python
from django.db import models


class SubjectProject(models.Model):
    interdisciplinary_project = models.ForeignKey(
        "academic.InterdisciplinaryProject",
        on_delete=models.CASCADE,
        related_name="subject_projects",
        verbose_name="Proyecto Interdisciplinario",
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="subject_projects",
        verbose_name="Oferta de Asignatura",
    )

    class Meta:
        app_label = "academic"
        verbose_name = "Asignatura del Proyecto"
        verbose_name_plural = "Asignaturas del Proyecto"
        unique_together = ("interdisciplinary_project", "subject_offering")

    def __str__(self):
        return f"{self.interdisciplinary_project.title} - {self.subject_offering}"
```

### Paso 5.4: Actualizar `__init__.py` de academic

```python
# ...existing imports...
from .interdisciplinary_project import InterdisciplinaryProject
from .subject_project import SubjectProject
```

### Paso 5.5: Migrar

```bash
python manage.py makemigrations academic --settings=config.settings.local
python manage.py migrate academic --settings=config.settings.local
```

### ✅ Criterio de éxito

- `Academic_Period.period_type` existe
- `InterdisciplinaryProject` y `SubjectProject` creados
- `python manage.py check` sin errores

---

## Fase 6 — App `attendance` (SRP: asistencia + conducta + socioemocional)

> **Objetivo:** Crear la app `attendance` moviendo modelos desde `grading` y agregando los nuevos.
>
> **Principios:** S (attendance = asistencia, conducta y desarrollo socioemocional), O (modelos extensibles)

### Paso 6.1: Mover `Attendance` a `attendance`

**Crear:** `apps/attendance/models/attendance.py`

```python
import uuid
from django.db import models


class Attendance(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID")
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
        null=True,
    )
    teacher_subject_section = models.ForeignKey(
        "academic.Teacher_Subject_Section",
        on_delete=models.CASCADE,
        verbose_name="Clase",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    attendance_status = models.ForeignKey(
        "attendance.AttendanceStatus",
        on_delete=models.PROTECT,
        verbose_name="Estado",
        null=True,
    )
    attendance_date = models.DateField(verbose_name="Fecha", null=True)
    absence_type = models.CharField(
        max_length=30, null=True, blank=True,
        choices=[
            ("justified", "Justificada"),
            ("unjustified", "Injustificada"),
            ("late", "Atraso"),
            ("none", "Sin falta"),
        ],
        verbose_name="Tipo de ausencia",
    )
    observation = models.TextField(null=True, blank=True, verbose_name="Observaciones")
    sync_status = models.CharField(max_length=20, default="pending", verbose_name="Estado de Sincronización")
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Sincronizado en")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    sync_version = models.PositiveIntegerField(default=0, verbose_name="Versión de Sincronización")
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")

    class Meta:
        app_label = "attendance"
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        unique_together = ("enrollment", "teacher_subject_section", "attendance_date")
        indexes = [
            models.Index(fields=["enrollment", "academic_period"]),
            models.Index(fields=["teacher_subject_section", "attendance_date"]),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.attendance_date} - {self.attendance_status}"
```

### Paso 6.2: Mover `AttendanceStatus` a `attendance`

**Crear:** `apps/attendance/models/attendance_status.py`

```python
from django.db import models


class AttendanceStatus(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")

    class Meta:
        app_label = "attendance"
        verbose_name = "Estado de Asistencia"
        verbose_name_plural = "Estados de Asistencia"
        ordering = ["name"]

    def __str__(self):
        return self.name
```

### Paso 6.3: Crear `IncidentType`

**Archivo:** `apps/attendance/models/incident_type.py`

```python
from django.db import models


class IncidentType(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")

    class Meta:
        app_label = "attendance"
        verbose_name = "Tipo de Incidente"
        verbose_name_plural = "Tipos de Incidente"
        ordering = ["name"]

    def __str__(self):
        return self.name
```

### Paso 6.4: Mover `ConductIncident` y mejorar

**Crear:** `apps/attendance/models/conduct_incident.py`

```python
import uuid
from django.db import models


class ConductIncident(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID")
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        verbose_name="Matrícula",
        null=True,
    )
    reported_by_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Reportado por",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        verbose_name="Período Académico",
    )
    incident_type = models.ForeignKey(
        "attendance.IncidentType",
        on_delete=models.PROTECT,
        verbose_name="Tipo de incidente",
        null=True,
    )
    incident_date = models.DateField(verbose_name="Fecha del Incidente")
    severity = models.IntegerField(verbose_name="Gravedad")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    actions_taken = models.TextField(null=True, blank=True, verbose_name="Acciones tomadas")
    family_notified = models.BooleanField(default=False, verbose_name="Familia Notificada")
    sync_status = models.CharField(max_length=20, default="pending", verbose_name="Estado de Sincronización")
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Sincronizado el")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    sync_version = models.PositiveIntegerField(default=0, verbose_name="Versión de Sincronización")
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")

    class Meta:
        app_label = "attendance"
        verbose_name = "Incidente de Conducta"
        verbose_name_plural = "Incidentes de Conducta"

    def __str__(self):
        return f"{self.enrollment} - {self.incident_type} ({self.incident_date})"
```

### Paso 6.5: Crear `SocioemotionalSkill`

**Archivo:** `apps/attendance/models/socioemotional_skill.py`

```python
from django.db import models


class SocioemotionalSkill(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    active = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        app_label = "attendance"
        verbose_name = "Habilidad Socioemocional"
        verbose_name_plural = "Habilidades Socioemocionales"
        ordering = ["name"]

    def __str__(self):
        return self.name
```

### Paso 6.6: Crear `SkillEvaluation`

**Archivo:** `apps/attendance/models/skill_evaluation.py`

```python
from django.db import models


class SkillEvaluation(models.Model):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="skill_evaluations",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        related_name="skill_evaluations",
        verbose_name="Período Académico",
    )
    socioemotional_skill = models.ForeignKey(
        "attendance.SocioemotionalSkill",
        on_delete=models.CASCADE,
        related_name="evaluations",
        verbose_name="Habilidad",
    )
    qualitative_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        verbose_name="Escala Cualitativa",
    )
    observation = models.TextField(null=True, blank=True, verbose_name="Observación")
    evaluation_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Evaluación")

    class Meta:
        app_label = "attendance"
        verbose_name = "Evaluación de Habilidad"
        verbose_name_plural = "Evaluaciones de Habilidades"
        unique_together = ("enrollment", "academic_period", "socioemotional_skill")

    def __str__(self):
        return f"{self.enrollment} - {self.socioemotional_skill.name}"
```

### Paso 6.7: Mover `BehaviorEvaluation` a `attendance` y mejorar

**Crear:** `apps/attendance/models/behavior_evaluation.py`

```python
from django.db import models


class BehaviorEvaluation(models.Model):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="attendance_behavior_evaluations",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        related_name="attendance_behavior_evaluations",
        verbose_name="Período Académico",
    )
    calculated_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        related_name="attendance_calculated_evaluations",
        verbose_name="Escala Calculada",
    )
    final_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="attendance_final_evaluations",
        verbose_name="Escala Final",
    )
    general_observation = models.TextField(null=True, blank=True, verbose_name="Observación general")
    override_reason = models.TextField(null=True, blank=True, verbose_name="Razón de anulación")

    class Meta:
        app_label = "attendance"
        verbose_name = "Evaluación de Conducta"
        verbose_name_plural = "Evaluaciones de Conducta"
        unique_together = ("enrollment", "academic_period")

    def __str__(self):
        return f"{self.enrollment} - {self.academic_period} ({self.calculated_scale})"
```

### Paso 6.8: Crear `__init__.py` de attendance models

```python
from .attendance import Attendance
from .attendance_status import AttendanceStatus
from .incident_type import IncidentType
from .conduct_incident import ConductIncident
from .socioemotional_skill import SocioemotionalSkill
from .skill_evaluation import SkillEvaluation
from .behavior_evaluation import BehaviorEvaluation

__all__ = [
    "Attendance", "AttendanceStatus", "IncidentType",
    "ConductIncident", "SocioemotionalSkill", "SkillEvaluation",
    "BehaviorEvaluation",
]
```

### Paso 6.9: Crear `apps/attendance/apps.py`

```python
from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.attendance"
    verbose_name = "Asistencia y Conducta"
```

### Paso 6.10: Crear `apps/attendance/urls.py`

```python
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = router.urls
```

### Paso 6.11: Eliminar modelos duplicados de `grading`

1. Eliminar de `apps/grading/models/`:
   - `attendance.py`
   - `attendance_status.py`
   - `conduct_incident.py`
   - `behavior_evaluation.py`

2. Actualizar `apps/grading/models/__init__.py`:

```python
from .student_note import StudentNote
from .grade_type import GradeType
from .qualitative_scale import QualitativeScale
from .evaluation_macro import EvaluationMacro
from .evaluation_criteria import EvaluationCriteria
from .evaluation_subcriteria import EvaluationSubcriteria
from .class_assignment import ClassAssignment
from .grade_change_history import GradeChangeHistory
from .period_grade_summary import PeriodGradeSummary
from .recovery_process import RecoveryProcess
from .diagnostic_evaluation import DiagnosticEvaluation
from .project_note import ProjectNote
```

### Paso 6.12: Configurar URLs globales

**Archivo:** `config/urls.py`

Agregar:

```python
path("api/attendance/", include("apps.attendance.urls")),
```

### Paso 6.13: Migrar

```bash
python manage.py makemigrations attendance grading --settings=config.settings.local
python manage.py migrate --settings=config.settings.local
```

### ✅ Criterio de éxito

- `attendance` app con 7 modelos funcionando
- `grading` reducida a 8 modelos
- `ConductIncident.category` reemplazado por `incident_type` FK
- Importaciones actualizadas en repositorios/servicios
- `python manage.py check` sin errores

---

## Fase 7 — Evaluaciones y Calificaciones (SRP: grading)

> **Objetivo:** Crear modelos faltantes de evaluación en `grading`.
>
> **Principios:** S (grading = evaluaciones, calificaciones, recuperación)

### Paso 7.1: Crear `PeriodGradeSummary`

**Archivo:** `apps/grading/models/period_grade_summary.py`

```python
from django.db import models


class PeriodGradeSummary(models.Model):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="grade_summaries",
        verbose_name="Matrícula",
    )
    subject_offering = models.ForeignKey(
        "academic.SubjectOffering",
        on_delete=models.CASCADE,
        related_name="grade_summaries",
        verbose_name="Oferta de Asignatura",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        related_name="grade_summaries",
        verbose_name="Período Académico",
    )
    formative_avg = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Promedio Formativo"
    )
    summative_avg = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Promedio Sumativo"
    )
    final_avg_truncated = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Promedio Final Truncado"
    )
    qualitative_scale = models.ForeignKey(
        "grading.QualitativeScale",
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Escala Cualitativa",
    )
    requires_recovery = models.BooleanField(default=False, verbose_name="Requiere Recuperación")
    promotion_status = models.CharField(
        max_length=20,
        null=True, blank=True,
        choices=[
            ("approved", "Aprobado"),
            ("failed", "Reprobado"),
            ("recovery", "En Recuperación"),
        ],
        verbose_name="Estado de Promoción",
    )
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="Calculado en")

    class Meta:
        app_label = "grading"
        verbose_name = "Resumen de Calificaciones del Período"
        verbose_name_plural = "Resúmenes de Calificaciones del Período"
        unique_together = ("enrollment", "subject_offering", "academic_period")

    def __str__(self):
        return f"{self.enrollment} - {self.subject_offering} ({self.academic_period})"
```

### Paso 7.2: Crear `RecoveryProcess`

**Archivo:** `apps/grading/models/recovery_process.py`

```python
from django.db import models


class RecoveryProcess(models.Model):
    period_grade_summary = models.ForeignKey(
        "grading.PeriodGradeSummary",
        on_delete=models.CASCADE,
        related_name="recovery_processes",
        verbose_name="Resumen de Calificaciones",
    )
    managed_by_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="recovery_processes",
        verbose_name="Gestionado por",
    )
    process_type = models.CharField(
        max_length=30,
        choices=[
            ("reinforcement", "Refuerzo"),
            ("improvement", "Evaluación de Mejora"),
            ("extraordinary", "Examen Extraordinario"),
        ],
        verbose_name="Tipo de proceso",
    )
    initial_grade = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota Inicial")
    reinforcement_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Nota de Refuerzo",
    )
    improvement_eval_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Nota de Evaluación de Mejora",
    )
    final_calculated_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Nota Final Calculada",
    )
    family_notified = models.BooleanField(default=False, verbose_name="Familia Notificada")
    start_date = models.DateField(verbose_name="Fecha de inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
    observations = models.TextField(null=True, blank=True, verbose_name="Observaciones")

    class Meta:
        app_label = "grading"
        verbose_name = "Proceso de Recuperación"
        verbose_name_plural = "Procesos de Recuperación"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.period_grade_summary} - {self.process_type}"
```

### Paso 7.3: Crear `DiagnosticEvaluation`

**Archivo:** `apps/grading/models/diagnostic_evaluation.py`

```python
from django.db import models


class DiagnosticEvaluation(models.Model):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="diagnostic_evaluations",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        related_name="diagnostic_evaluations",
        verbose_name="Período Académico",
    )
    applied_by_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="diagnostic_evaluations",
        verbose_name="Aplicada por",
    )
    socioemotional_area = models.CharField(max_length=100, verbose_name="Área socioemocional")
    findings_description = models.TextField(verbose_name="Descripción de hallazgos")
    development_level = models.CharField(max_length=50, verbose_name="Nivel de desarrollo")
    application_date = models.DateField(verbose_name="Fecha de aplicación")
    recommendations = models.TextField(null=True, blank=True, verbose_name="Recomendaciones")

    class Meta:
        app_label = "grading"
        verbose_name = "Evaluación Diagnóstica"
        verbose_name_plural = "Evaluaciones Diagnósticas"
        ordering = ["-application_date"]

    def __str__(self):
        return f"{self.enrollment} - {self.socioemotional_area} ({self.application_date})"
```

### Paso 7.4: Crear `ProjectNote`

**Archivo:** `apps/grading/models/project_note.py`

```python
import uuid
from django.db import models


class ProjectNote(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID")
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="project_notes",
        verbose_name="Matrícula",
    )
    interdisciplinary_project = models.ForeignKey(
        "academic.InterdisciplinaryProject",
        on_delete=models.CASCADE,
        related_name="project_notes",
        verbose_name="Proyecto Interdisciplinario",
    )
    product_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota del producto"
    )
    presentation_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota de exposición"
    )
    final_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Nota final"
    )
    observation = models.TextField(null=True, blank=True, verbose_name="Observación")
    sync_status = models.CharField(max_length=20, default="pending", verbose_name="Estado de Sincronización")
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Sincronizado el")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    sync_version = models.PositiveIntegerField(default=0, verbose_name="Versión de Sincronización")
    device_origin = models.CharField(max_length=40, null=True, blank=True, verbose_name="Dispositivo de Origen")

    class Meta:
        app_label = "grading"
        verbose_name = "Nota de Proyecto"
        verbose_name_plural = "Notas de Proyectos"
        unique_together = ("enrollment", "interdisciplinary_project")

    def __str__(self):
        return f"{self.enrollment} - {self.interdisciplinary_project.title} ({self.final_score})"
```

### Paso 7.5: Migrar

```bash
python manage.py makemigrations grading --settings=config.settings.local
python manage.py migrate grading --settings=config.settings.local
```

### ✅ Criterio de éxito

- 4 nuevos modelos en `grading`
- `python manage.py check` sin errores
- Migraciones aplicadas

---

## Fase 8 — Analítica y Alertas (SRP: analytics)

> **Objetivo:** Corregir FKs en modelos de analytics y crear `EarlyAlert`.
>
> **Principios:** S (analytics = predicción + alertas), D (depende de students y academic)

### Paso 8.1: Corregir FK en `StudentFeatureSnapshot`

**Archivo:** `apps/analytics/models/student_feature_snapshot.py`

Cambiar:

```python
    student = models.ForeignKey("students.Student", ...)
```

Por:

```python
    enrollment = models.ForeignKey("students.Enrollment", on_delete=models.CASCADE, verbose_name="Matrícula")
```

Y agregar campos faltantes:

```python
    justified_absences = models.IntegerField(default=0, verbose_name="Ausencias justificadas")
    unjustified_absences = models.IntegerField(default=0, verbose_name="Ausencias injustificadas")
    formative_avg_normalized = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Promedio formativo normalizado")
    summative_avg_normalized = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Promedio sumativo normalizado")
    severe_incidents_count = models.IntegerField(default=0, verbose_name="Incidentes graves")
    is_repeat = models.BooleanField(default=False, verbose_name="Es repitente")
    has_special_needs = models.BooleanField(default=False, verbose_name="Tiene NEE")
    residential_zone = models.CharField(max_length=50, blank=True, verbose_name="Zona de residencia")
    distance_to_school_km = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Distancia al colegio (km)")
    active_alerts = models.IntegerField(default=0, verbose_name="Alertas activas")
```

### Paso 8.2: Corregir FK en `StudentRiskScore`

**Archivo:** `apps/analytics/models/student_risk_score.py`

Cambiar:

```python
    student = models.ForeignKey("students.Student", ...)
```

Por:

```python
    enrollment = models.ForeignKey("students.Enrollment", on_delete=models.CASCADE, verbose_name="Matrícula")
```

### Paso 8.3: Crear `EarlyAlert`

**Archivo:** `apps/analytics/models/early_alert.py`

```python
from django.db import models


class EarlyAlert(models.Model):
    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="early_alerts",
        verbose_name="Matrícula",
    )
    academic_period = models.ForeignKey(
        "academic.Academic_Period",
        on_delete=models.CASCADE,
        related_name="early_alerts",
        verbose_name="Período Académico",
    )
    alert_type = models.CharField(
        max_length=50,
        choices=[
            ("low_attendance", "Baja Asistencia"),
            ("failing_grades", "Calificaciones Bajas"),
            ("behavioral", "Problemas de Conducta"),
            ("dropout_risk", "Riesgo de Deserción"),
            ("socioemotional", "Problemas Socioemocionales"),
        ],
        verbose_name="Tipo de alerta",
    )
    description = models.TextField(verbose_name="Descripción")
    urgency_level = models.CharField(
        max_length=20,
        choices=[
            ("low", "Baja"),
            ("medium", "Media"),
            ("high", "Alta"),
            ("critical", "Crítica"),
        ],
        verbose_name="Nivel de urgencia",
    )
    attended = models.BooleanField(default=False, verbose_name="Atendida")
    attended_by_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="attended_alerts",
        verbose_name="Atendida por",
    )
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de detección")
    attended_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de atención")
    response_actions = models.TextField(null=True, blank=True, verbose_name="Acciones de respuesta")

    class Meta:
        app_label = "analytics"
        verbose_name = "Alerta Temprana"
        verbose_name_plural = "Alertas Tempranas"
        ordering = ["-detected_at"]
        indexes = [
            models.Index(fields=["attended", "urgency_level"]),
            models.Index(fields=["enrollment", "academic_period"]),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.enrollment} ({self.get_urgency_level_display()})"
```

### Paso 8.4: Actualizar `__init__.py` de analytics

```python
from .student_risk_score import StudentRiskScore
from .student_risk_factor import StudentRiskFactor
from .student_feature_snapshot import StudentFeatureSnapshot
from .risk_factor import RiskFactor
from .early_alert import EarlyAlert

__all__ = ["StudentRiskScore", "StudentRiskFactor", "StudentFeatureSnapshot", "RiskFactor", "EarlyAlert"]
```

### Paso 8.5: Migrar

```bash
python manage.py makemigrations analytics --settings=config.settings.local
python manage.py migrate analytics --settings=config.settings.local
```

### ✅ Criterio de éxito

- `StudentFeatureSnapshot` apunta a `Enrollment`
- `StudentRiskScore` apunta a `Enrollment`
- `EarlyAlert` creado con todos los campos
- Migraciones de datos para FKs si hay registros existentes
- `python manage.py check` sin errores

---

## Fase 9 — Repositorios (Capa de Datos)

> **Objetivo:** Crear/actualizar repositorios para todos los modelos nuevos y movidos.
>
> **Principios:** D (repositorios abstraen ORM), O (extensibles vía herencia)

### Paso 9.1: Crear repositorio base (si no existe)

**Archivo:** `apps/core/repositories/base.py`

```python
from django.db import models


class BaseRepository:
    """Repositorio base con operaciones CRUD genéricas."""

    model = None  # Debe ser definido en subclases

    @classmethod
    def get_by_id(cls, id):
        return cls.model.objects.filter(id=id).first()

    @classmethod
    def get_by_uuid(cls, uuid):
        return cls.model.objects.filter(uuid=uuid).first()

    @classmethod
    def list(cls, **filters):
        return cls.model.objects.filter(**filters)

    @classmethod
    def create(cls, **data):
        return cls.model.objects.create(**data)

    @classmethod
    def update(cls, id, **data):
        cls.model.objects.filter(id=id).update(**data)
        return cls.get_by_id(id)

    @classmethod
    def delete(cls, id):
        return cls.model.objects.filter(id=id).delete()

    @classmethod
    def exists(cls, **filters):
        return cls.model.objects.filter(**filters).exists()

    @classmethod
    def count(cls, **filters):
        return cls.model.objects.filter(**filters).count()
```

### Paso 9.2: Repositorios para `attendance`

**Archivo:** `apps/attendance/repositories/attendance_repository.py`

```python
from apps.core.repositories.base import BaseRepository
from apps.attendance.models import Attendance


class AttendanceRepository(BaseRepository):
    model = Attendance

    @classmethod
    def get_by_enrollment_and_period(cls, enrollment_id, academic_period_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
        ).select_related("attendance_status")

    @classmethod
    def get_absences_summary(cls, enrollment_id, academic_period_id):
        from django.db.models import Count, Q
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
        ).aggregate(
            total=Count("id"),
            justified=Count("id", filter=Q(absence_type="justified")),
            unjustified=Count("id", filter=Q(absence_type="unjustified")),
            late=Count("id", filter=Q(absence_type="late")),
        )
```

**Archivo:** `apps/attendance/repositories/conduct_incident_repository.py`

```python
from apps.core.repositories.base import BaseRepository
from apps.attendance.models import ConductIncident


class ConductIncidentRepository(BaseRepository):
    model = ConductIncident

    @classmethod
    def get_by_enrollment_and_period(cls, enrollment_id, academic_period_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
            academic_period_id=academic_period_id,
        ).select_related("incident_type")
```

### Paso 9.3: Repositorios para `grading` (nuevos modelos)

**Archivo:** `apps/grading/repositories/period_grade_summary_repository.py`

```python
from apps.core.repositories.base import BaseRepository
from apps.grading.models import PeriodGradeSummary


class PeriodGradeSummaryRepository(BaseRepository):
    model = PeriodGradeSummary

    @classmethod
    def get_by_enrollment(cls, enrollment_id):
        return cls.model.objects.filter(
            enrollment_id=enrollment_id,
        ).select_related("subject_offering", "academic_period", "qualitative_scale")
```

**Archivo:** `apps/grading/repositories/recovery_process_repository.py`

```python
from apps.core.repositories.base import BaseRepository
from apps.grading.models import RecoveryProcess


class RecoveryProcessRepository(BaseRepository):
    model = RecoveryProcess

    @classmethod
    def get_active_by_enrollment(cls, enrollment_id):
        return cls.model.objects.filter(
            period_grade_summary__enrollment_id=enrollment_id,
            end_date__isnull=True,
        )
```

### Paso 9.4: Repositorios para `analytics`

**Archivo:** `apps/analytics/repositories/early_alert_repository.py`

```python
from apps.core.repositories.base import BaseRepository
from apps.analytics.models import EarlyAlert


class EarlyAlertRepository(BaseRepository):
    model = EarlyAlert

    @classmethod
    def get_pending_alerts(cls, urgency_level=None):
        filters = {"attended": False}
        if urgency_level:
            filters["urgency_level"] = urgency_level
        return cls.model.objects.filter(**filters).select_related("enrollment", "academic_period")

    @classmethod
    def get_by_enrollment(cls, enrollment_id):
        return cls.model.objects.filter(enrollment_id=enrollment_id).order_by("-detected_at")
```

### ✅ Criterio de éxito

- Repositorios creados para modelos nuevos
- `BaseRepository` implementado en `core`
- Métodos específicos por dominio (asistencia, alertas, etc.)

---

## Fase 10 — Servicios (Capa de Negocio)

> **Objetivo:** Implementar servicios con lógica de negocio para los nuevos modelos.
>
> **Principios:** S (servicios con responsabilidad única), D (dependen de repositorios, no de modelos directo)

### Paso 10.1: Servicio de cálculo de `PeriodGradeSummary`

**Archivo:** `apps/grading/services/grade_calculation_service.py`

```python
from decimal import Decimal, ROUND_DOWN
from django.db import transaction
from apps.grading.repositories.period_grade_summary_repository import PeriodGradeSummaryRepository


class GradeCalculationService:
    """Servicio para cálculo de promedios y resúmenes de calificaciones."""

    @staticmethod
    @transaction.atomic
    def calculate_period_summary(enrollment, subject_offering, academic_period):
        """
        Calcula el resumen de calificaciones para una matrícula,
        oferta de asignatura y período académico específicos.
        """
        from apps.grading.models import StudentNote, ClassAssignment

        # Obtener todas las notas del estudiante en ese período
        notes = StudentNote.objects.filter(
            enrollment=enrollment,
            class_assignment__evaluation_subcriteria__evaluation_criteria__evaluation_macro__academic_period=academic_period,
            class_assignment__subject_offering=subject_offering,
            manually_overridden=False,
        )

        # Calcular promedios (lógica de negocio específica)
        # ... (implementar según reglas del Ministerio de Educación)

        summary, created = PeriodGradeSummaryRepository.create(
            enrollment=enrollment,
            subject_offering=subject_offering,
            academic_period=academic_period,
            formative_avg=Decimal("0.00"),
            summative_avg=Decimal("0.00"),
            final_avg_truncated=Decimal("0.00"),
            requires_recovery=False,
        )
        return summary
```

### Paso 10.2: Servicio de alertas tempranas

**Archivo:** `apps/analytics/services/early_alert_service.py`

```python
from django.db import transaction
from apps.analytics.repositories.early_alert_repository import EarlyAlertRepository


class EarlyAlertService:
    """Servicio para generación y gestión de alertas tempranas."""

    @staticmethod
    @transaction.atomic
    def evaluate_student_risk(enrollment, academic_period):
        """
        Evalúa si un estudiante debe generar una alerta temprana
        basado en reglas de negocio predefinidas.
        """
        alerts = []

        # Regla 1: Baja asistencia
        # ... (implementar reglas)

        # Regla 2: Calificaciones bajas
        # ... (implementar reglas)

        # Regla 3: Incidentes de conducta graves
        # ... (implementar reglas)

        return alerts

    @staticmethod
    def mark_as_attended(alert_id, user_id, actions=None):
        """Marca una alerta como atendida."""
        alert = EarlyAlertRepository.get_by_id(alert_id)
        if alert and not alert.attended:
            EarlyAlertRepository.update(
                alert.id,
                attended=True,
                attended_by_user_id=user_id,
                attended_at=...,
                response_actions=actions,
            )
        return alert
```

### ✅ Criterio de éxito

- Servicios creados con lógica de negocio inicial
- Servicios dependen de repositorios, no de modelos directos
- Operaciones atómicas via `@transaction.atomic`

---

## Fase 11 — APIs (Capa de Presentación)

> **Objetivo:** Crear ViewSets para los nuevos modelos siguiendo las convenciones del proyecto.
>
> **Principios:** I (action_permissions específicos), D (views dependen de services)

### Paso 11.1: ViewSet para `EarlyAlert`

**Archivo:** `apps/analytics/api/views.py`

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.analytics.models import EarlyAlert
from apps.analytics.api.serializers import EarlyAlertSerializer
from apps.analytics.repositories.early_alert_repository import EarlyAlertRepository
from apps.analytics.services.early_alert_service import EarlyAlertService
from apps.core.permissions import HasPermission
from apps.core.utils import ok_response, error_response
from apps.core.pagination import StandardResultsSetPagination
from apps.core.constants.permissions import analytics as perm


class EarlyAlertViewSet(viewsets.ModelViewSet):
    queryset = EarlyAlert.objects.all()
    serializer_class = EarlyAlertSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, HasPermission]
    action_permissions = {
        "list": perm.VIEW_ALERT,
        "retrieve": perm.VIEW_ALERT,
        "create": perm.CREATE_ALERT,
        "update": perm.UPDATE_ALERT,
        "partial_update": perm.UPDATE_ALERT,
        "destroy": perm.DELETE_ALERT,
        "mark_attended": perm.UPDATE_ALERT,
    }

    @action(detail=True, methods=["post"])
    def mark_attended(self, request, pk=None):
        alert = self.get_object()
        actions = request.data.get("response_actions", "")
        alert = EarlyAlertService.mark_as_attended(
            alert.id, request.user.id, actions
        )
        if alert:
            return ok_response(
                EarlyAlertSerializer(alert).data,
                msg="Alerta marcada como atendida",
            )
        return error_response("Alerta no encontrada")
```

### ✅ Criterio de éxito

- ViewSets creados para `EarlyAlert`, `PeriodGradeSummary`, `RecoveryProcess`, etc.
- `action_permissions` definidos
- Paginación con `StandardResultsSetPagination`
- Respuestas con `ok_response`/`error_response`

---

## Fase 12 — Rutas y URLs

> **Objetivo:** Registrar todas las nuevas rutas de API.

### Paso 12.1: URLs de `attendance`

**Archivo:** `apps/attendance/urls.py`

```python
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = router.urls
```

### Paso 12.2: URLs globales

**Archivo:** `config/urls.py`

```python
from django.urls import path, include

urlpatterns = [
    # ...existing paths...
    path("api/attendance/", include("apps.attendance.urls")),
]
```

### ✅ Criterio de éxito

- Todas las rutas registradas
- `python manage.py check` sin errores
- `/api/attendance/` accesible

---

## Fase 13 — Tests (Validación)

> **Objetivo:** Escribir tests que validen la integridad de la reestructuración.
>
> **Nota:** Usar `django.test.TestCase` + `APIClient`, NO pytest.

### Paso 13.1: Test de integridad de modelos

**Archivo:** `apps/core/tests/test_model_integrity.py`

```python
from django.test import TestCase
from django.apps import apps


class ModelIntegrityTest(TestCase):
    """Verifica que todos los modelos esperados existen."""

    def test_attendance_models_exist(self):
        """La app attendance debe tener 7 modelos."""
        app_models = apps.get_app_config("attendance").get_models()
        model_names = [m.__name__ for m in app_models]
        expected = [
            "Attendance", "AttendanceStatus", "IncidentType",
            "ConductIncident", "SocioemotionalSkill", "SkillEvaluation",
            "BehaviorEvaluation",
        ]
        for name in expected:
            with self.subTest(model=name):
                self.assertIn(name, model_names)

    def test_grading_models_count(self):
        """Grading debe tener exactamente 12 modelos."""
        app_models = apps.get_app_config("grading").get_models()
        self.assertEqual(len(list(app_models)), 12)
```

### ✅ Criterio de éxito

- Tests de integridad pasan
- Tests existentes siguen pasando
- `python manage.py test --settings=config.settings.test` sin fallos

---

## Apéndice A: Dependencias entre Fases

```
Fase 0 (Preparación)
    │
    ▼
Fase 1 (Core / SyncQueue)
    │
    ▼
Fase 2 (Institutions / Section) ──────┐
    │                                  │
    ▼                                  ▼
Fase 3 (Accounts)                 Fase 4 (Students)
    │                                  │
    ▼                                  ▼
Fase 5 (Academic) ────────────── Fase 6 (Attendance)
    │                                  │
    ▼                                  ▼
Fase 7 (Grading) ─────────────── Fase 8 (Analytics)
    │                                  │
    ▼                                  ▼
Fase 9 (Repositories) ←─────── Todas las anteriores
    │
    ▼
Fase 10 (Services) ←─────────── Fase 9
    │
    ▼
Fase 11 (APIs) ←──────────────── Fase 10
    │
    ▼
Fase 12 (URLs) ←──────────────── Fase 11
    │
    ▼
Fase 13 (Tests) ←────────────── Todas las anteriores
```

## Apéndice B: Checklist de Validación por Fase

```bash
# Ejecutar después de CADA fase:
python manage.py check --settings=config.settings.local
python manage.py makemigrations --dry-run --settings=config.settings.local  # Verificar migraciones
python manage.py test apps.core.tests.test_model_integrity --settings=config.settings.test  # Tests de integridad
```

## Apéndice C: Principios SOLID — Mapa de Aplicación

| Principio | Dónde se aplica                          | Cómo se garantiza                                  |
| --------- | ---------------------------------------- | -------------------------------------------------- |
| **S** RP  | 9 apps con 1 responsabilidad cada una    | Tabla de agrupación en Fase 0                      |
| **O** CP  | Repositorios + Servicios                 | `BaseRepository` extensible, servicios inyectables |
| **L** SP  | Repositorios heredan de `BaseRepository` | Misma interfaz CRUD en todos                       |
| **I** SP  | ViewSets con `action_permissions`        | Permisos granulares por acción                     |
| **D** IP  | API → Services → Repositories → Models   | Inversión de dependencias en capas                 |
