# Revisión de Modelos — Informe Final de Inconsistencias (v2)
**Proyecto:** Sistema de Gestión Escolar  
**Fecha de revisión:** 10 de junio de 2026  
**Scope:** 12 apps — academic, analytics, attendance, behavior, configuration, core, grading, iam, institutions, integration, people, students

---

## Inventario de Modelos

### Conteo original vs resultado

| Métrica | Valor |
|---|---|
| Apps revisadas | 12 |
| Modelos en el archivo original | **79** |
| Modelos eliminados | **0** |
| Modelos nuevos (nueva tabla) | **0** |
| Modelos resultado | **79** |
| Modelos con cambios de campo o método | **22** |

**No se elimina ni agrega ningún modelo.** Todos los 79 modelos tienen razón de ser en la infraestructura del sistema. Los cambios son correcciones de campos, `on_delete`, `null`, `related_name`, validaciones en `clean()` y métodos de estado.

### Inventario por app

| App | Modelos | Estado |
|---|---|---|
| `academic` | AcademicPeriod, ClassSchedule, DayOfWeek, InterdisciplinaryProject, PeriodType, Subject, SubjectAcademicConfig, SubjectOffering, SubjectProject, TeacherSubjectSection | ✅ Sin cambios estructurales |
| `analytics` | AlertType, DashboardMetric, EarlyAlert, RiskFactor, StudentFeatureSnapshot, StudentRiskFactor, StudentRiskScore, UrgencyLevel | 🔧 2 modelos con campos a corregir |
| `attendance` | AbsenceType, AttendanceStatus, Attendance | 🔧 1 modelo con campos y validación a corregir |
| `behavior` | BehaviorEvaluation, ConductIncident, DevelopmentLevel, DiagnosticEvaluation, IncidentType, Severity, SkillEvaluation, SocioemotionalArea, SocioemotionalSkill | 🔧 3 modelos con correcciones |
| `configuration` | SystemConfig | ✅ Sin cambios |
| `core` | AuditLog, TimeStampedModel | 🔧 1 modelo (TimeStampedModel) con corrección crítica |
| `grading` | ActivityType, BlockComponent, ComponentIndicator, EvaluationBlock, EvaluationType, EvaluativeActivity, GradeChangeHistory, GradeType, LearningReport, PeriodGradeSummary, ProjectNote, PromotionStatus, QualitativeScale, QualitativeScaleSublevel, RecoveryProcess, RecoveryProcessHistory, RecoveryProcessStatus, RecoveryProcessType, RecoverySession, StudentNote | 🔧 6 modelos con correcciones |
| `iam` | Permission, Role, RolePermission, User, UserRole | 🔧 3 modelos con correcciones |
| `institutions` | AcademicGrade, AcademicLevel, AcademicSublevel, SchoolYear, Section | 🔧 3 modelos con correcciones |
| `integration` | SyncableModel, SyncOperation, SyncQueue, SyncSchemaVersion, SyncStatus | 🔧 2 modelos con correcciones |
| `people` | DocumentType, Person | 🔧 1 modelo con correcciones |
| `students` | Enrollment, EnrollmentHistory, EnrollmentStatus, Kinship, ResidentialZone, SpecialNeedsType, Student, StudentRepresentative, WithdrawalReason | 🔧 3 modelos con correcciones |

---

## Convenciones

| Símbolo | Severidad |
|---|---|
| 🔴 **CRÍTICO** | Corrupción de datos, pérdida de información o sistema inoperable |
| 🟡 **IMPORTANTE** | No rompe hoy, pero causará problemas reales con datos en producción |
| 🟠 **DEUDA TÉCNICA** | Acumula complejidad, dificulta mantenimiento o evolución futura |

---

## App: `core`

### 🔴 CORE-1 — `TimeStampedModel.updated_at` con `default` en lugar de `auto_now`

**Modelo:** `TimeStampedModel.updated_at`  
**Impacto:** Afecta los 77 modelos concretos que heredan de `TimeStampedModel`. Con `default=timezone.now`, `updated_at` solo se establece al crear el registro y nunca se actualiza automáticamente. Toda la auditoría del sistema queda sin fecha real de última modificación.

```python
# ANTES:
updated_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Actualización")

# DESPUÉS:
updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
```
> ⚠️ Requiere migración. Con `auto_now=True` el campo deja de ser editable directamente.

---

## App: `grading`

### 🔴 GRADING-1 — `EvaluativeActivity` requiere `ComponentIndicator` obligatorio

**Modelo:** `EvaluativeActivity.component_indicator`  
**Problema:** La única FK al árbol de configuración apunta al nivel más profundo (Indicadores MINEDUC). Si secretaría no carga los indicadores, ningún docente puede crear actividades — el modelo transaccional más crítico queda bloqueado.

```python
# Agregar FK al nivel siempre disponible:
block_component = models.ForeignKey(
    "grading.BlockComponent",
    on_delete=models.PROTECT,
    verbose_name="Componente de Bloque",
)
# Hacer el indicador opcional:
component_indicator = models.ForeignKey(
    "grading.ComponentIndicator",
    on_delete=models.SET_NULL,
    null=True, blank=True,
    verbose_name="Indicador de Componente",
)
```

---

### 🔴 GRADING-2 — `EvaluationBlock.evaluation_type` con `on_delete=SET_NULL`

**Modelo:** `EvaluationBlock.evaluation_type`  
**Problema:** Si se elimina el tipo "FORMATIVO", todos los bloques formativos quedan con `evaluation_type=NULL`. El cálculo de `PeriodGradeSummary.formative_avg` y `summative_avg` falla silenciosamente.

```python
evaluation_type = models.ForeignKey(
    "grading.EvaluationType",
    on_delete=models.PROTECT,   # ← cambiar SET_NULL → PROTECT
    null=False,                  # ← quitar null=True
    verbose_name="Tipo de evaluación",
)
```

---

### 🔴 GRADING-3 — `StudentNote.unique_together` con FK nullable rompe unicidad en PostgreSQL

**Modelo:** `StudentNote`, `Meta.unique_together = [("enrollment", "evaluative_activity")]`  
**Problema:** PostgreSQL trata `NULL ≠ NULL`, por lo que la constraint no aplica cuando `evaluative_activity=NULL`. Permite dos notas sin actividad para el mismo estudiante.

```python
# Opción A — recomendada: quitar null
evaluative_activity = models.ForeignKey(
    "grading.EvaluativeActivity",
    on_delete=models.CASCADE,
    null=False,
    verbose_name="Actividad Evaluativa",
)

# Opción B — si null es necesario: constraint condicional
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=["enrollment", "evaluative_activity"],
            condition=models.Q(evaluative_activity__isnull=False),
            name="unique_enrollment_activity_notnull",
        )
    ]
```

---

### 🔴 GRADING-4 — `RecoveryProcess.managed_by_user` con `on_delete=CASCADE`

**Modelo:** `RecoveryProcess.managed_by_user`  
**Problema:** Si se elimina el docente gestor, el proceso de recuperación completo del estudiante (incluyendo `RecoverySession` e historial) se borra en cascada.

```python
managed_by_user = models.ForeignKey(
    "iam.User",
    on_delete=models.SET_NULL,   # ← CASCADE → SET_NULL
    null=True,
    related_name="recovery_processes",
    verbose_name="Gestionado por",
)
```

---

### 🟡 GRADING-5 — Sin validación de suma de pesos en `EvaluationBlock` y `BlockComponent`

**Modelos:** `EvaluationBlock.weight_percentage`, `BlockComponent.internal_weight`  
**Problema:** Nada impide que los bloques sumen 110% o los componentes 85%.

```python
# En EvaluationBlock.clean():
def clean(self):
    hermanos = EvaluationBlock.objects.filter(
        academic_period=self.academic_period,
        subject_offering=self.subject_offering,
        is_active=True,
    ).exclude(pk=self.pk)
    total = sum(b.weight_percentage for b in hermanos) + self.weight_percentage
    if total > Decimal("100.00"):
        raise ValidationError(f"Los bloques suman {total}% — deben sumar exactamente 100%")
# Misma lógica para BlockComponent dentro del mismo EvaluationBlock
```

---

### 🟡 GRADING-6 — `BlockComponent` sin `unique_together` por nombre dentro del bloque

**Modelo:** `BlockComponent`  
**Problema:** Permite crear el componente "Tareas" dos veces en el mismo bloque con diferentes pesos.

```python
class Meta:
    unique_together = [("evaluation_block", "name")]
```

---

### 🟡 GRADING-7 — `LearningReport` duplica campos de `PeriodGradeSummary`

**Modelos:** `LearningReport`, `PeriodGradeSummary`  
**Problema:** `formative_avg`, `summative_avg` y `final_avg` existen en ambos modelos. Dos fuentes de verdad para la misma nota. `LearningReport` debería referenciar o derivar de `PeriodGradeSummary`.

---

### 🟡 GRADING-8 — `ProjectNote.final_score` sin validación de consistencia

**Modelo:** `ProjectNote`  
**Problema:** `final_score` puede no ser consistente con `product_score + presentation_score`.

```python
def clean(self):
    expected = (self.product_score + self.presentation_score) / 2
    if abs(self.final_score - expected) > Decimal("0.01"):
        raise ValidationError(
            "final_score no es consistente con product_score y presentation_score"
        )
```

---

### 🟡 GRADING-9 — `EvaluativeActivity.is_interdisciplinary_project` booleano desconectado

**Modelo:** `EvaluativeActivity.is_interdisciplinary_project`  
**Problema:** El flag no tiene FK al `InterdisciplinaryProject` correspondiente. Ambigüedad entre usar `StudentNote` o `ProjectNote`.

```python
# Reemplazar:
interdisciplinary_project = models.ForeignKey(
    "academic.InterdisciplinaryProject",
    on_delete=models.SET_NULL,
    null=True, blank=True,
    verbose_name="Proyecto Interdisciplinario",
)
# Eliminar: is_interdisciplinary_project = BooleanField(...)
```

---

### 🟠 GRADING-10 — `PeriodGradeSummary` asume exactamente 2 tipos de evaluación

**Modelo:** `PeriodGradeSummary.formative_avg`, `summative_avg`  
**Problema:** Si el Ministerio introduce un tercer tipo con peso en nota final, el modelo no lo soporta sin migración de esquema.

---

## App: `behavior`

### 🔴 BEHAVIOR-1 — `DiagnosticEvaluation.applied_by_user` con `on_delete=CASCADE`

**Modelo:** `DiagnosticEvaluation.applied_by_user`  
**Problema:** Si se elimina el usuario aplicador, la evaluación diagnóstica completa del estudiante desaparece.

```python
applied_by_user = models.ForeignKey(
    "iam.User",
    on_delete=models.SET_NULL,   # ← CASCADE → SET_NULL
    null=True,
    related_name="diagnostic_evaluations",
    verbose_name="Aplicada por",
)
```

---

### 🟡 BEHAVIOR-2 — `BehaviorEvaluation` con `related_name` incorrecto

**Modelo:** `BehaviorEvaluation.enrollment`, `BehaviorEvaluation.academic_period`  
**Problema:** Ambos `related_name` tienen el prefijo `attendance_` que corresponde a otra app. Genera confusión en queries y navegación inversa.

```python
enrollment = models.ForeignKey(
    "students.Enrollment",
    related_name="behavior_evaluations",   # ← quitar prefijo "attendance_"
    ...
)
academic_period = models.ForeignKey(
    "academic.AcademicPeriod",
    related_name="behavior_evaluations",   # ← quitar prefijo "attendance_"
    ...
)
```

---

### 🟡 BEHAVIOR-3 — `StudentRepresentative` sin vigencia temporal

**Modelo:** `StudentRepresentative`  
**Problema:** Si un estudiante cambia de representante, no hay forma de saber desde cuándo ni hasta cuándo era válida la relación anterior. El representante anterior sigue con acceso indefinido.

```python
valid_from = models.DateField(
    default=date.today,
    verbose_name="Válido desde",
)
valid_until = models.DateField(
    null=True, blank=True,
    verbose_name="Válido hasta",
)
```

---

## App: `attendance`

### 🟡 ATTENDANCE-1 — `attendance_status` y `attendance_date` con `null=True`

**Modelo:** `Attendance.attendance_status`, `Attendance.attendance_date`  
**Problema:** Un registro de asistencia sin estado o sin fecha no tiene significado semántico válido. Ambos son campos centrales y obligatorios.

```python
attendance_status = models.ForeignKey(
    "attendance.AttendanceStatus",
    on_delete=models.PROTECT,
    null=False,   # ← quitar null=True
    verbose_name="Estado",
)
attendance_date = models.DateField(
    null=False,   # ← quitar null=True
    verbose_name="Fecha",
)
```

---

### 🟡 ATTENDANCE-2 — Sin validación de que `attendance_date` esté dentro del período

**Modelo:** `Attendance`  
**Problema:** Nada impide fecha de 2019 en un período activo de 2026, ni que el `academic_period` no corresponda al `school_year` de la clase.

```python
def clean(self):
    period = self.academic_period
    if self.attendance_date and not (period.start_date <= self.attendance_date <= period.end_date):
        raise ValidationError(
            f"La fecha {self.attendance_date} no está dentro del período "
            f"{period.name} ({period.start_date} – {period.end_date})"
        )
    school_year_docente = self.teacher_subject_section.subject_offering.school_year
    if period.school_year != school_year_docente:
        raise ValidationError(
            "El período académico no pertenece al mismo año escolar que la clase"
        )
```

---

## App: `institutions`

### 🟡 INSTITUTIONS-1 — `AcademicGrade.academic_sublevel` con `null=True`

**Modelo:** `AcademicGrade.academic_sublevel`  
**Problema:** Un grado sin subnivel hace que `academic_level` devuelva `None`, rompiendo `QualitativeScaleSublevel`.

```python
academic_sublevel = models.ForeignKey(
    "institutions.AcademicSublevel",
    on_delete=models.PROTECT,
    null=False,   # ← quitar null=True, blank=True
    verbose_name="Subnivel Académico",
)
```

---

### 🟡 INSTITUTIONS-2 — `Section.academic_grade` con `null=True`

**Modelo:** `Section.academic_grade`  
**Problema:** Una sección sin grado no puede determinar qué materias le corresponden.

```python
academic_grade = models.ForeignKey(
    "institutions.AcademicGrade",
    on_delete=models.CASCADE,
    null=False,   # ← quitar null=True
    verbose_name="Grado Académico",
)
```

---

### 🟡 INSTITUTIONS-3 — `SchoolYear` sin validación de solapamiento de fechas

**Modelo:** `SchoolYear`  
**Problema:** Pueden coexistir dos años escolares activos con fechas superpuestas.

```python
def clean(self):
    solapados = SchoolYear.objects.filter(
        is_active=True,
        start_date__lt=self.end_date,
        end_date__gt=self.start_date,
    ).exclude(pk=self.pk)
    if solapados.exists():
        raise ValidationError(
            "Ya existe un año escolar activo que se solapa con estas fechas"
        )
```

---

## App: `analytics`

### 🟡 ANALYTICS-1 — `StudentFeatureSnapshot.enrollment` y `StudentRiskScore.enrollment` con `null=True` marcado "temporal"

**Modelos:** `StudentFeatureSnapshot.enrollment`, `StudentRiskScore.enrollment`  
**Problema:** Comentario dice `# Permite null temporal`. Si llegó a producción, hay snapshots sin matrícula que el modelo ML ignora silenciosamente.

```python
enrollment = models.ForeignKey(
    "students.Enrollment",
    on_delete=models.CASCADE,
    null=False,   # ← eliminar null=True y comentario "temporal"
    verbose_name="Matrícula",
)
```

---

### 🟡 ANALYTICS-2 — `DashboardMetric.metric_value` JSONField sin validación de versión de esquema

**Modelo:** `DashboardMetric.metric_value`, `DashboardMetric.metric_schema_version`  
**Problema:** El campo `metric_schema_version` existe pero no hay validación que garantice que `metric_value` sea consistente con esa versión. Un dashboard que asume schema `1.0` puede fallar silenciosamente con datos de schema `2.0`.

**Corrección sugerida:** Validadores por versión en la capa de servicio que lean `metric_schema_version` antes de deserializar `metric_value`.

---

## App: `iam`

### 🔴 IAM-1 — `Role.code` con `null=True` en campo semántico único

**Modelo:** `Role.code`  
**Problema:** PostgreSQL permite múltiples NULL en columnas `unique`. La propiedad `User.user_category` depende de `role.code`; si es NULL devuelve `"OTRO"` silenciosamente.

```python
code = models.CharField(
    max_length=50,
    unique=True,
    null=False,   # ← quitar null=True
    verbose_name="Código del Rol",
)
```

---

### 🔴 IAM-2 — `User.person` con `null=True` sin validación por tipo de usuario

**Modelo:** `User.person`  
**Problema:** Un usuario sin `person` no tiene nombre real en reportes ni auditoría. Solo `create_superuser` justifica `person=null`.

```python
def clean(self):
    if not self.is_superuser and not self.person_id:
        raise ValidationError(
            "Todo usuario no-superusuario debe tener una Persona asociada"
        )
```

---

### 🟡 IAM-3 — `UserRole.expires_at` no verificado en `has_perm()`

**Modelo:** `UserRole.expires_at`, `User.has_perm()`  
**Problema:** Un rol expirado sigue otorgando permisos indefinidamente.

```python
def has_perm(self, permission_code):
    if self.is_superuser:
        return True
    now = timezone.now()
    return self.user_roles.filter(
        role__role_permissions__permission__code=permission_code,
    ).filter(
        models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
    ).exists()
```

---

### 🟡 IAM-4 — Vínculo `User → Student` y `User → StudentRepresentative` indirecto y sin constraint

**Modelos:** `User`, `Student`, `StudentRepresentative`  
**Problema:** El vínculo pasa por `User.person → Person ← Student.person`. No hay FK directa ni constraint que garantice unicidad. Dado que estudiantes y representantes tienen su propio usuario, el vínculo debe ser explícito.

```python
# En Student:
user = models.OneToOneField(
    "iam.User",
    on_delete=models.SET_NULL,
    null=True, blank=True,
    related_name="student_profile",
    verbose_name="Usuario",
)

# En StudentRepresentative (o en una entidad Representative separada):
user = models.OneToOneField(
    "iam.User",
    on_delete=models.SET_NULL,
    null=True, blank=True,
    related_name="representative_profile",
    verbose_name="Usuario",
)
```

Con esto el acceso es directo y sin ambigüedad:
```python
request.user.student_profile.enrollments.all()
request.user.representative_profile.student_set.all()
```

---

### 🟠 IAM-5 — `User.generate_username()` con condición de carrera en entornos concurrentes

**Modelo:** `User.generate_username()`  
**Problema:** Verifica si el username existe y luego lo asigna en dos pasos separados. En entornos con múltiples workers, dos usuarios con el mismo nombre base pueden recibir el mismo username antes de que ninguno haga `save()`.

**Corrección sugerida:** Capturar `IntegrityError` en `save()` y reintentar la generación del username.

---

## App: `students`

### 🔴 STUDENTS-1 — `Student.person` con `null=True`

**Modelo:** `Student.person`  
**Problema:** Un estudiante sin `person` es un registro vacío sin nombre, documento ni identificación. `get_full_name()` y `get_age()` devuelven vacíos silenciosamente.

```python
person = models.OneToOneField(
    "people.Person",
    on_delete=models.CASCADE,
    null=False,   # ← quitar null=True, blank=True
    verbose_name="Persona",
)
```

---

### 🟡 STUDENTS-2 — `StudentRepresentative.person` con `null=True`

**Modelo:** `StudentRepresentative.person`  
**Problema:** La relación estudiante-representante puede existir sin persona asociada. Sin `person` no hay nombre, teléfono ni correo — imposible contactar al representante.

```python
person = models.ForeignKey(
    "people.Person",
    on_delete=models.CASCADE,
    null=False,   # ← quitar null=True, blank=True
    related_name="student_representatives",
    verbose_name="Persona",
)
```

---

### 🟠 STUDENTS-3 — `Enrollment.save()` con guard `hasattr` que siempre es `True`

**Modelo:** `Enrollment.save()`  
**Problema:** `hasattr(self, "school_year")` siempre es `True` (es un campo del modelo). La primera condición es código muerto.

```python
def save(self, *args, **kwargs):
    if self.school_year_id is None:   # ← reemplazar el hasattr por esto
        if self.section and self.section.school_year_id:
            self.school_year = self.section.school_year
    super().save(*args, **kwargs)
```

---

## App: `people`

### 🟡 PEOPLE-1 — `Person.document_type` con `null=True`

**Modelo:** `Person.document_type`  
**Problema:** Una persona sin tipo de documento hace inconsistente la identificación documental. `document_number` es único y obligatorio pero `document_type` no.

```python
document_type = models.ForeignKey(
    "people.DocumentType",
    on_delete=models.PROTECT,
    null=False,   # ← quitar null=True
    verbose_name="Tipo de Documento",
)
```

---

### 🟠 PEOPLE-2 — `Person.email` con `blank=True` pero sin `null=True`

**Modelo:** `Person.email`  
**Problema:** `email` puede ser `""` pero es `EmailField`. Si en el futuro se añade `unique=True`, múltiples registros con `email=""` colisionarán. El estándar Django para campos opcionales es `null=True, blank=True`.

```python
email = models.EmailField(
    null=True,
    blank=True,
    verbose_name="Correo Electrónico",
)
```

---

## App: `integration`

### 🟡 INTEGRATION-1 — `SyncQueue.idempotency_key` incluye `attempts` en el hash

**Modelo:** `SyncQueue.save()`  
**Problema:** Incluir `attempts` en el hash hace que cada reintento genere una `idempotency_key` diferente, **rompiendo la idempotencia por diseño**.

```python
# ANTES:
raw = f"{self.source_table}:{self.record_uuid}:{op_code}:{self.attempts}"

# DESPUÉS:
raw = f"{self.source_table}:{self.record_uuid}:{op_code}"
```

---

### 🟡 INTEGRATION-2 — `SyncableModel` — métodos de estado no llaman `save()`

**Modelo:** `SyncableModel.mark_synced()`, `mark_conflict()`, `mark_error()`  
**Problema:** Los tres métodos modifican atributos en memoria pero no persisten. Cualquier llamada sin un `save()` posterior deja el estado sin guardar.

```python
def mark_synced(self):
    self.sync_status = SyncStatusChoices.SYNCED
    self.synced_at = timezone.now()
    self.save(update_fields=["sync_status", "synced_at"])

def mark_conflict(self):
    self.sync_status = SyncStatusChoices.CONFLICT
    self.save(update_fields=["sync_status"])

def mark_error(self):
    self.sync_status = SyncStatusChoices.ERROR
    self.save(update_fields=["sync_status"])
```

---

## Problemas descartados (diseño correcto confirmado)

| Ítem | Razón del descarte |
|---|---|
| `ConductIncident` sin FK a `TeacherSubjectSection` | Un incidente puede ocurrir fuera del aula (recreo, pasillo, acto). Cualquier usuario puede reportarlo sin estar vinculado a una sección. Diseño correcto. |
| Sin modelo `Institution` para director | Sistema de una sola institución. El director tiene acceso global. No aplica multitenancy. |

---

## Resumen ejecutivo por app

| App | Modelos totales | 🔴 Crítico | 🟡 Importante | 🟠 Deuda | Modelos afectados |
|---|---|---|---|---|---|
| `grading` | 20 | 4 | 5 | 1 | EvaluativeActivity, EvaluationBlock, StudentNote, RecoveryProcess, BlockComponent, LearningReport, ProjectNote, PeriodGradeSummary |
| `behavior` | 9 | 1 | 2 | 0 | DiagnosticEvaluation, BehaviorEvaluation, StudentRepresentative |
| `iam` | 5 | 2 | 2 | 1 | Role, User, UserRole |
| `students` | 9 | 1 | 1 | 1 | Student, StudentRepresentative, Enrollment |
| `institutions` | 5 | 0 | 3 | 0 | AcademicGrade, Section, SchoolYear |
| `attendance` | 3 | 0 | 2 | 0 | Attendance |
| `analytics` | 8 | 0 | 2 | 0 | StudentFeatureSnapshot, StudentRiskScore |
| `integration` | 5 | 0 | 2 | 0 | SyncQueue, SyncableModel |
| `people` | 2 | 0 | 1 | 1 | Person |
| `core` | 2 | 1 | 0 | 0 | TimeStampedModel |
| `academic` | 10 | 0 | 0 | 0 | — |
| `configuration` | 1 | 0 | 0 | 0 | — |
| **TOTAL** | **79** | **8** | **20** | **3** | **22 modelos con cambios** |

---

## Orden de atención recomendado

### Sprint inmediato
1. **CORE-1** — `updated_at` con `default` en lugar de `auto_now`. Afecta toda la auditoría del sistema desde el primer registro.
2. **GRADING-1, GRADING-2, GRADING-3, GRADING-4** — Integridad del módulo más crítico y de mayor volumen transaccional.
3. **IAM-1, IAM-2, STUDENTS-1** — Identidad correcta de todos los actores del sistema.

### Próximo sprint
4. **BEHAVIOR-1** — Evaluación clínica no puede perderse por baja de usuario.
5. **INTEGRATION-1, INTEGRATION-2** — La idempotencia rota y los métodos sin `save()` afectan toda la sincronización offline.
6. **IAM-4** — FK directa `User → Student` y `User → StudentRepresentative` para acceso limpio por rol.

### Backlog estructural
7. Validaciones de negocio: GRADING-5, GRADING-8, ATTENDANCE-2, INSTITUTIONS-3.
8. Campos obligatorios: ATTENDANCE-1, INSTITUTIONS-1, INSTITUTIONS-2, ANALYTICS-1, STUDENTS-2, PEOPLE-1.
9. Deuda técnica: GRADING-10, IAM-5, STUDENTS-3, PEOPLE-2.
