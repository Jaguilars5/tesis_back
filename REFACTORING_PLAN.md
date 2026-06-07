# Plan de Refactorización: Reorganización de Apps Django

## Estado Actual vs Estado Deseado

### Apps Actuales (14 apps)
```
apps/
├── accounts/       → User, Person, UserRole, Role, Permission, RolePermission
├── academic/       → Modelos académicos (OK)
├── analytics/      → Modelos de análisis (OK)
├── attendance/     → Attendance + modelos de comportamiento (MEZCLADO)
├── behavior/       → Vacía (lista para crear)
├── catalogs/       → Solo DocumentType y Kinship (INCOMPLETA)
├── core/           → SystemConfig, SyncQueue (DEBERÍAN IR A OTRAS APPS)
├── grading/        → Calificaciones + catálogos (MEZCLADO)
├── institutions/   → Modelos institucionales (OK)
├── integration/    → Vacía (lista para crear)
├── people/         → Person ya existe con estructura completa
└── students/       → Modelos de estudiantes (OK)
```

### Apps Deseadas (13 apps)
```
apps/
├── iam/            → User, Role, Permission, UserRole, RolePermission
├── people/         → Person (ya existe)
├── catalogs/       → DocumentType, GradeType, QualitativeScale, AttendanceStatus, IncidentType
├── institutions/   → SchoolYear, AcademicLevel, AcademicGrade, Section
├── students/       → StudentProfile, FamilyLink, Enrollment, EnrollmentStatus
├── academic/       → AcademicPeriod, Subject, SubjectConfig, SubjectOffering, TeacherAssignment, InterdisciplinaryProject, SubjectProject
├── grading/        → EvaluationBlock, BlockComponent, ComponentIndicator, EvaluativeActivity, StudentNote, ProjectNote, RecoveryProcess, GradeChangeHistory, PeriodGradeSummary
├── attendance/     → Attendance (solo registro de asistencia)
├── behavior/       → SocioemotionalSkill, ConductIncident, SkillEvaluation, DiagnosticEvaluation, BehaviorEvaluation, PeriodBehaviorSummary
├── analytics/      → EarlyAlert, StudentFeatureSnapshot, StudentRiskScore, RiskFactor
├── configuration/  → SystemConfig
├── integration/    → SyncQueue
└── core/           → Utilidades compartidas (sin modelos de dominio)
```

## Orden de Migración (Considerando Dependencias)

### Fase 1: Apps Independientes (Sin dependencias críticas)
1. **configuration/** - Mover SystemConfig desde core/
2. **integration/** - Mover SyncQueue desde core/

### Fase 2: Catálogos (Referenciados por otras apps)
3. **catalogs/** - Expandir con GradeType, QualitativeScale, AttendanceStatus, IncidentType

### Fase 3: Identidad y Acceso
4. **iam/** - Crear desde accounts/ (User, Role, Permission, UserRole, RolePermission)
5. **people/** - Consolidar Person (ya existe, eliminar de accounts/)

### Fase 4: Comportamiento
6. **behavior/** - Mover modelos desde attendance/ y grading/

### Fase 5: Limpieza
7. **attendance/** - Limpiar dejando solo Attendance
8. **grading/** - Limpiar dejando solo modelos de calificación
9. **accounts/** - Eliminar o mantener como wrapper de iam/ + people/

## Plan Detallado por App

---

### 1. CONFIGURATION (Nueva)

**Origen:** `apps/core/models/system_config.py`  
**Destino:** `apps/configuration/models/system_config.py`

#### Estructura:
```
apps/configuration/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py
├── models/
│   ├── __init__.py
│   └── system_config.py
├── api/
│   ├── __init__.py
│   ├── serializers/
│   ├── views/
│   └── urls.py
├── services/
│   ├── __init__.py
│   └── config_service.py
├── repositories/
│   ├── __init__.py
│   └── config_repository.py
└── migrations/
    └── __init__.py
```

#### Pasos:
1. Crear estructura de directorios
2. Mover `system_config.py` desde `core/models/`
3. Cambiar `app_label = "core"` → `app_label = "configuration"`
4. Actualizar `AUTH_USER_MODEL` si es necesario
5. Crear migración: `python manage.py makemigrations configuration`
6. Migrar datos: `python manage.py migrate configuration`
7. Actualizar importaciones en todo el proyecto

---

### 2. INTEGRATION (Nueva)

**Origen:** `apps/core/models/sync_queue.py`  
**Destino:** `apps/integration/models/sync_queue.py`

#### Estructura:
```
apps/integration/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py
├── models/
│   ├── __init__.py
│   └── sync_queue.py
├── api/
│   ├── __init__.py
│   ├── serializers/
│   ├── views/
│   └── urls.py
├── services/
│   ├── __init__.py
│   └── sync_service.py
├── repositories/
│   ├── __init__.py
│   └── sync_repository.py
├── tasks/
│   ├── __init__.py
│   └── sync_tasks.py
└── migrations/
    └── __init__.py
```

#### Pasos:
1. Crear estructura de directorios
2. Mover `sync_queue.py` desde `core/models/`
3. Cambiar `app_label = "core"` → `app_label = "integration"`
4. Crear migración: `python manage.py makemigrations integration`
5. Migrar datos: `python manage.py migrate integration`
6. Actualizar importaciones

---

### 3. CATALOGS (Expandir)

**Origen:**
- `apps/grading/models/grade_type.py`
- `apps/grading/models/qualitative_scale.py`
- `apps/attendance/models/attendance_status.py`
- `apps/attendance/models/incident_type.py`

**Destino:** `apps/catalogs/models/`

#### Estructura:
```
apps/catalogs/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py
├── models/
│   ├── __init__.py
│   ├── document_type.py          (ya existe en document_type/models/)
│   ├── grade_type.py             (desde grading/)
│   ├── qualitative_scale.py      (desde grading/)
│   ├── attendance_status.py      (desde attendance/)
│   └── incident_type.py          (desde attendance/)
├── api/
│   ├── __init__.py
│   ├── serializers/
│   ├── views/
│   └── urls.py
├── services/
│   ├── __init__.py
│   └── catalog_service.py
├── repositories/
│   ├── __init__.py
│   └── catalog_repository.py
└── migrations/
    └── __init__.py
```

#### Pasos:
1. Mover modelos desde grading/ y attendance/
2. Cambiar `app_label` en cada modelo:
   - `app_label = "grading"` → `app_label = "catalogs"`
   - `app_label = "attendance"` → `app_label = "catalogs"`
3. Actualizar `models/__init__.py`
4. Crear migraciones: `python manage.py makemigrations catalogs`
5. Migrar datos: `python manage.py migrate catalogs`
6. Actualizar todas las referencias ForeignKey en otras apps

---

### 4. IAM (Nueva - desde accounts/)

**Origen:** `apps/accounts/models/` (User, Role, Permission, UserRole, RolePermission)  
**Destino:** `apps/iam/models/`

#### Estructura:
```
apps/iam/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── role.py
│   ├── permission.py
│   ├── user_role.py
│   └── role_permission.py
├── api/
│   ├── __init__.py
│   ├── serializers/
│   │   ├── __init__.py
│   │   ├── user_serializer.py
│   │   ├── role_serializer.py
│   │   └── permission_serializer.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── user_viewset.py
│   │   ├── role_viewset.py
│   │   └── permission_viewset.py
│   └── urls.py
├── services/
│   ├── __init__.py
│   ├── user_service.py
│   ├── role_service.py
│   └── auth_service.py
├── repositories/
│   ├── __init__.py
│   ├── user_repository.py
│   └── role_repository.py
├── managers/
│   ├── __init__.py
│   └── user_manager.py
└── migrations/
    └── __init__.py
```

#### Pasos:
1. Crear estructura de directorios
2. Mover modelos desde accounts/ (excepto Person)
3. Cambiar `app_label = "accounts"` → `app_label = "iam"`
4. Actualizar `AUTH_USER_MODEL = "iam.User"` en settings
5. Mover managers (UserManager)
6. Mover api/, services/, repositories/ desde accounts/
7. Crear migraciones: `python manage.py makemigrations iam`
8. Migrar datos: `python manage.py migrate iam`
9. Actualizar todas las referencias en todo el proyecto

**⚠️ CRÍTICO:** Cambiar `AUTH_USER_MODEL` requiere migración cuidadosa de la base de datos.

---

### 5. PEOPLE (Consolidar)

**Estado:** Ya existe con estructura completa  
**Acción:** Eliminar Person de accounts/

#### Pasos:
1. Verificar que `apps/people/models/person.py` tiene `app_label = "people"`
2. Eliminar `apps/accounts/models/person.py`
3. Actualizar `apps/accounts/models/__init__.py` para remover Person
4. Actualizar `apps/iam/models/user.py` para referenciar `"people.Person"` en lugar de `"Person"`
5. Actualizar todas las referencias ForeignKey en otras apps:
   - `"accounts.Person"` → `"people.Person"`
6. Crear migración: `python manage.py makemigrations people iam`
7. Migrar datos: `python manage.py migrate people iam`

---

### 6. BEHAVIOR (Nueva - desde attendance/ y grading/)

**Origen:**
- `apps/attendance/models/socioemotional_skill.py`
- `apps/attendance/models/conduct_incident.py`
- `apps/attendance/models/skill_evaluation.py`
- `apps/attendance/models/behavior_evaluation.py`
- `apps/attendance/models/incident_type.py` → Va a catalogs/
- `apps/grading/models/diagnostic_evaluation.py`

**Destino:** `apps/behavior/models/`

#### Estructura:
```
apps/behavior/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py
├── models/
│   ├── __init__.py
│   ├── socioemotional_skill.py
│   ├── conduct_incident.py
│   ├── skill_evaluation.py
│   ├── behavior_evaluation.py
│   ├── diagnostic_evaluation.py
│   └── period_behavior_summary.py  (si existe)
├── api/
│   ├── __init__.py
│   ├── serializers/
│   ├── views/
│   └── urls.py
├── services/
│   ├── __init__.py
│   └── behavior_service.py
├── repositories/
│   ├── __init__.py
│   └── behavior_repository.py
└── migrations/
    └── __init__.py
```

#### Pasos:
1. Crear estructura de directorios
2. Mover modelos desde attendance/ y grading/
3. Cambiar `app_label` en cada modelo:
   - `app_label = "attendance"` → `app_label = "behavior"`
   - `app_label = "grading"` → `app_label = "behavior"`
4. Actualizar `models/__init__.py`
5. Crear api/, services/, repositories/
6. Crear migraciones: `python manage.py makemigrations behavior`
7. Migrar datos: `python manage.py migrate behavior`
8. Actualizar todas las referencias ForeignKey

---

### 7. ATTENDANCE (Limpiar)

**Acción:** Eliminar modelos que se movieron a behavior/ y catalogs/

#### Modelos que quedan:
- `Attendance` (registro_asistencia)

#### Modelos que se van:
- `AttendanceStatus` → catalogs/
- `IncidentType` → catalogs/
- `ConductIncident` → behavior/
- `SocioemotionalSkill` → behavior/
- `SkillEvaluation` → behavior/
- `BehaviorEvaluation` → behavior/

#### Pasos:
1. Eliminar archivos de modelos movidos
2. Actualizar `models/__init__.py`
3. Eliminar api/, services/, repositories/ de modelos movidos
4. Crear migración: `python manage.py makemigrations attendance`
5. Migrar datos: `python manage.py migrate attendance`

---

### 8. GRADING (Limpiar)

**Acción:** Eliminar modelos que se movieron a catalogs/ y behavior/

#### Modelos que quedan:
- `EvaluationBlock` (bloque_evaluacion)
- `BlockComponent` (componente_bloque)
- `ComponentIndicator` (indicador_componente)
- `EvaluativeActivity` (actividad_evaluativa)
- `StudentNote` (nota_actividad)
- `ProjectNote` (nota_proyecto)
- `RecoveryProcess` (proceso_recuperacion)
- `GradeChangeHistory` (auditoria_nota)
- `PeriodGradeSummary` (resumen_calificacion_periodo)

#### Modelos que se van:
- `GradeType` → catalogs/
- `QualitativeScale` → catalogs/
- `DiagnosticEvaluation` → behavior/

#### Pasos:
1. Eliminar archivos de modelos movidos
2. Actualizar `models/__init__.py`
3. Actualizar ForeignKey que referencian modelos movidos
4. Crear migración: `python manage.py makemigrations grading`
5. Migrar datos: `python manage.py migrate grading`

---

### 9. ACCOUNTS (Eliminar o Mantener)

**Opción A: Eliminar completamente**
- Mover todo a iam/ y people/
- Eliminar directorio accounts/
- Actualizar INSTALLED_APPS

**Opción B: Mantener como wrapper**
- Mantener accounts/ como app que importa de iam/ y people/
- Útil para compatibilidad con código existente
- Desaconsejado: crea confusión

**Recomendación:** Eliminar completamente después de migrar todo.

#### Pasos:
1. Verificar que todos los modelos se movieron a iam/ y people/
2. Verificar que todas las importaciones se actualizaron
3. Eliminar directorio apps/accounts/
4. Actualizar INSTALLED_APPS en settings
5. Eliminar migraciones antiguas de accounts/

---

## Actualización de Settings

### config/settings/base.py

```python
LOCAL_APPS = [
    "apps.core",
    "apps.iam",              # Nuevo
    "apps.people",           # Nuevo
    "apps.catalogs",         # Nuevo
    "apps.institutions",
    "apps.students",
    "apps.academic",
    "apps.grading",
    "apps.attendance",
    "apps.behavior",         # Nuevo
    "apps.analytics",
    "apps.configuration",    # Nuevo
    "apps.integration",      # Nuevo
]

# Actualizar AUTH_USER_MODEL
AUTH_USER_MODEL = "iam.User"  # Cambiado de "accounts.User"
```

---

## Actualización de URLs

### config/urls.py

```python
urlpatterns = [
    path("api/accounts/", include("apps.iam.urls")),      # Cambiado
    path("api/people/", include("apps.people.urls")),     # Nuevo
    path("api/catalogs/", include("apps.catalogs.urls")), # Nuevo
    path("api/academic/", include("apps.academic.urls")),
    path("api/institutions/", include("apps.institutions.urls")),
    path("api/grading/", include("apps.grading.urls")),
    path("api/students/", include("apps.students.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/attendance/", include("apps.attendance.urls")),
    path("api/behavior/", include("apps.behavior.urls")), # Nuevo
    path("api/configuration/", include("apps.configuration.urls")), # Nuevo
    path("api/integration/", include("apps.integration.urls")),     # Nuevo
]
```

---

## Estrategia de Migración de Base de Datos

### Opción 1: Migración en Vivo (Recomendado para desarrollo)
1. Crear nuevas apps con estructuras vacías
2. Mover modelos una app a la vez
3. Crear migraciones para cada app
4. Ejecutar migraciones incrementalmente
5. Actualizar código gradualmente

### Opción 2: Migración por ContentTypes (Para producción con datos)
1. Crear nuevas apps
2. Usar `django.contrib.contenttypes` para preservar relaciones
3. Migrar datos con scripts personalizados
4. Validar integridad referencial

### Opción 3: Dump/Load (Solo para desarrollo)
1. `python manage.py dumpdata > data.json`
2. Refactorizar código
3. `python manage.py migrate`
4. `python manage.py loaddata data.json`

**Recomendación:** Usar Opción 1 para desarrollo, Opción 2 para producción.

---

## Checklist de Verificación

### Después de cada fase:
- [ ] `python manage.py check` pasa sin errores
- [ ] `python manage.py makemigrations` no crea migraciones inesperadas
- [ ] `python manage.py migrate` se ejecuta sin errores
- [ ] `python manage.py test --settings=config.settings.test` pasa todos los tests
- [ ] `python manage.py runserver` inicia sin errores
- [ ] API endpoints funcionan correctamente
- [ ] Admin de Django funciona correctamente
- [ ] No hay importaciones rotas

### Al final de la refactorización:
- [ ] Todas las apps tienen estructura completa (api/, models/, services/, repositories/)
- [ ] No hay modelos huérfanos en apps incorrectas
- [ ] Todas las ForeignKey apuntan a las apps correctas
- [ ] AUTH_USER_MODEL está actualizado
- [ ] INSTALLED_APPS está actualizado
- [ ] URLs están actualizadas
- [ ] Tests pasan al 100%
- [ ] Documentación actualizada (README.md, STRUCTURE.md en cada app)

---

## Orden de Ejecución Recomendado

```bash
# Fase 1: Configuración e Integración
python manage.py startapp configuration apps/configuration
python manage.py startapp integration apps/integration
# Mover modelos y crear migraciones

# Fase 2: Catálogos
# Expandir catalogs/ con modelos de grading/ y attendance/

# Fase 3: IAM y People
python manage.py startapp iam apps/iam
# Mover modelos de accounts/ a iam/
# Consolidar people/

# Fase 4: Behavior
python manage.py startapp behavior apps/behavior
# Mover modelos de attendance/ y grading/ a behavior/

# Fase 5: Limpieza
# Limpiar attendance/ y grading/
# Eliminar accounts/

# Fase 6: Actualización final
# Actualizar settings, urls, importaciones
# Ejecutar tests
```

---

## Riesgos y Consideraciones

### ⚠️ Alto Riesgo:
1. **Cambiar AUTH_USER_MODEL** - Requiere migración cuidadosa
2. **ForeignKey entre apps** - Puede romper integridad referencial
3. **Migraciones de producción** - Requiere plan de rollback

### ⚠️ Medio Riesgo:
1. **Importaciones circulares** - Verificar dependencias
2. **Tests rotos** - Actualizar todos los tests
3. **API endpoints** - Actualizar URLs y viewsets

### ✅ Bajo Riesgo:
1. **Mover modelos sin dependencias** (configuration, integration)
2. **Expandir catalogs/** (modelos independientes)
3. **Reorganizar estructura de directorios**

---

## Próximos Pasos Inmediatos

1. **Revisar este plan** y ajustar según necesidades específicas
2. **Hacer backup de la base de datos** antes de comenzar
3. **Crear rama git** para la refactorización
4. **Comenzar con Fase 1** (configuration, integration)
5. **Validar cada fase** antes de continuar con la siguiente

---

## Notas Finales

- **No ejecutar en producción** sin pruebas exhaustivas
- **Mantener rama git** con el código antiguo como referencia
- **Documentar cada cambio** en commits descriptivos
- **Probar en staging** antes de desplegar a producción
- **Considerar migración gradual** si hay muchos datos
