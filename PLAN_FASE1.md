# Plan de Implementación - Fase 1: Corrección Estructural

**Proyecto:** Sistema de Gestión Académica - Back
**Fase:** 1 de 8
**Fecha:** 2026-06-08
**Dependencia:** Fase 0 (Preparación) completada

---

## 1. Resumen Ejecutivo

Esta fase corrige la consistencia estructural mínima del modelo mediante la corrección de PK, FK, cardinalidades, nulabilidad, unicidad y relaciones faltantes o ambiguas. Sin una estructura correcta, no es viable estabilizar el dominio académico ni garantizar la integridad referencial.

### Objetivos Específicos

1. Eliminar/validar la dependencia circular entre `AcademicSublevel` y `AcademicGrade`
2. Corregir la relación autorreferente de `AcademicPeriod`
3. Normalizar `QualitativeScale.applicable_sublevel` de texto libre a FK
4. Hacer obligatoria la FK `StudentNote.enrollment`
5. Rediseñar `SystemConfig` (PK textual y `updated_at` duplicado)
6. Definir restricciones de unicidad compuestas faltantes
7. Crear tablas puente explícitas para relaciones M2M con atributos

---

## 2. Inventario de Cambios Requeridos

### 2.1 Corrección de Modelos Existentes

| # | Modelo | Campo/Problema | Acción | Prioridad |
|---|--------|----------------|--------|-----------|
| 1 | `SystemConfig` | PK textual (`key` CharField) | Agregar `id` auto-increment, usar como PK | Alta |
| 2 | `SystemConfig` | `updated_at` duplicado | Eliminar campo (TimeStampedModel ya lo provee) | Alta |
| 3 | `QualitativeScale` | `applicable_sublevel` CharField | Crear FK o tabla puente a `AcademicSublevel` | Alta |
| 4 | `StudentNote` | `enrollment` nullable | Hacer no nulo después de validar datos | Alta |
| 5 | `AcademicPeriod` | Posible autorreferencia `parent_period` | Investigar esquema físico, agregar si existe | Media |
| 6 | `AcademicGrade` | FK a `AcademicSublevel` con `null=True` | Validar si debe ser obligatorio | Media |

### 2.2 Restricciones de Unicidad Faltantes

| # | Modelo | Unique Together | Campos | Prioridad |
|---|--------|-----------------|--------|-----------|
| 1 | `SubjectAcademicConfig` | `(subject, academic_grade)` | subject, academic_grade | Alta |
| 2 | `Section` | `(school_year, academic_grade, parallel)` | school_year, academic_grade, parallel | Alta |
| 3 | `TeacherSubjectSection` | `(user, subject_offering)` | user, subject_offering | Alta |
| 4 | `StudentNote` | `(enrollment, evaluative_activity)` | enrollment, evaluative_activity | Media |

### 2.3 Tablas Puente a Crear

| # | Tabla | Propósito | Modelos Conectados |
|---|-------|-----------|-------------------|
| 1 | `QualitativeScaleSublevel` | Escala cualitativa aplicable a subniveles | `QualitativeScale` <-> `AcademicSublevel` |

---

## 3. Detalle de Cambios por Archivo

### 3.1 `apps/configuration/models/system_config.py`

**Cambio 1:** Agregar campo `id` auto-increment como PK
```python
# Estado actual
class SystemConfig(TimeStampedModel):
    key = models.CharField(max_length=255, primary_key=True)

# Nuevo estado
class SystemConfig(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(max_length=255, unique=True)
```

**Cambio 2:** Eliminar campo `updated_at` duplicado
- El campo `updated_at` ya existe en `TimeStampedModel`
- Remover `updated_at = models.DateTimeField(auto_now=True)` de la clase

**Migración requerida:**
- Crear migración que:
  1. Agregue columna `id` como serial/bigserial
  2. Copie `key` existente a columna temporal
  3. Elimine `key` como PK
  4. Agregue `id` como nueva PK
  5. Agregue constraint unique a `key`
  6. Elimine columna `updated_at` duplicada

---

### 3.2 `apps/grading/models/qualitative_scale.py`

**Cambio:** Normalizar `applicable_sublevel` de CharField a relación con `AcademicSublevel`

**Opción A - FK Simple** (recomendada si 1:1 o 1:N):
```python
applicable_sublevel = models.ForeignKey(
    'institutions.AcademicSublevel',
    on_delete=models.PROTECT,
    null=True,
    blank=True
)
```

**Opción B - Tabla Puente** (si M2M, para agregar atributos):
```python
class QualitativeScaleSublevel(models.Model):
    scale = models.ForeignKey('QualitativeScale', on_delete=models.CASCADE)
    sublevel = models.ForeignKey('institutions.AcademicSublevel', on_delete=models.CASCADE)
    applies_to_grade_types = models.ManyToManyField('grading.GradeType', blank=True)
    
    class Meta:
        unique_together = ('scale', 'sublevel')
```

**Decisión:** Usar **Opción B** para soportar M2M y permitir atributos adicionales por escala-subnivel.

---

### 3.3 `apps/grading/models/student_note.py`

**Cambio:** Hacer `enrollment` no nulo

```python
# Estado actual
enrollment = models.ForeignKey(
    'students.Enrollment',
    on_delete=models.CASCADE,
    null=True,
    blank=True
)

# Nuevo estado
enrollment = models.ForeignKey(
    'students.Enrollment',
    on_delete=models.CASCADE,
    null=False,
    blank=False
)
```

**Pre-requisitos:**
1. Verificar que todos los registros tengan `enrollment` no nulo
2. Si existen registros sin enrollment, migrar datos o marcar como huérfanos
3. Ejecutar script de validación antes de la migración

---

### 3.4 `apps/academic/models/academic_period.py`

**Cambio:** Agregar autorreferencia `parent_period` (si existe en esquema físico)

```python
parent_period = models.ForeignKey(
    'self',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='child_periods'
)
```

**Investigación requerida:**
- Verificar en migración existente si existe columna `parent_period_id`
- Si existe: solo agregar el campo al modelo
- Si no existe: documentar que la autorreferencia no aplica

---

### 3.5 `apps/institutions/models/section.py`

**Cambio:** Agregar `unique_together`

```python
class Section(TimeStampedModel):
    # ... campos existentes ...
    
    class Meta:
        unique_together = [('school_year', 'academic_grade', 'parallel')]
```

---

### 3.6 `apps/academic/models/subject_academic_config.py`

**Cambio:** Agregar `unique_together`

```python
class SubjectAcademicConfig(TimeStampedModel):
    # ... campos existentes ...
    
    class Meta:
        unique_together = [('subject', 'academic_grade')]
```

---

### 3.7 `apps/academic/models/teacher_subject_section.py`

**Cambio:** Agregar `unique_together`

```python
class TeacherSubjectSection(TimeStampedModel):
    # ... campos existentes ...
    
    class Meta:
        unique_together = [('user', 'subject_offering')]
```

---

### 3.8 `apps/grading/models/student_note.py`

**Cambio:** Agregar `unique_together`

```python
class StudentNote(TimeStampedModel):
    # ... campos existentes ...
    
    class Meta:
        unique_together = [('enrollment', 'evaluative_activity')]
```

---

## 4. Secuencia de Migraciones

### Orden de ejecución (para minimizar riesgos de rollback)

```
┌─────────────────────────────────────────────────────────────────┐
│ Paso 1: SystemConfig - Agregar PK id y eliminar updated_at    │
│   - Migrations: 0002_add_pk_remove_updated_at                  │
│   - Riesgo: BAJO - Datos existentes se preservan               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Paso 2: QualitativeScale - Crear tabla puente                  │
│   - Migrations: 0002_create_bridge_table                       │
│   - Riesgo: BAJO - Solo crea nueva tabla                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Paso 3: Section - Agregar unique_together                      │
│   - Migrations: 0002_add_unique_constraint                      │
│   - Riesgo: MEDIO - Verificar duplicados antes                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Paso 4: SubjectAcademicConfig - Agregar unique_together         │
│   - Migrations: 0002_add_unique_constraint                      │
│   - Riesgo: BAJO - Verificar duplicados antes                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Paso 5: TeacherSubjectSection - Agregar unique_together         │
│   - Migrations: 0002_add_unique_constraint                      │
│   - Riesgo: BAJO - Verificar duplicados antes                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Paso 6: StudentNote - Hacer enrollment no nulo                  │
│   - Migrations: 0003_make_enrollment_required                   │
│   - Riesgo: ALTO - Validar datos primero                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Paso 7: AcademicPeriod - Agregar parent_period (si aplica)       │
│   - Migrations: 0002_add_parent_period                          │
│   - Riesgo: BAJO - Solo agrega columna nullable                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Scripts de Validación Pre-Migración

### 5.1 Script: Validar SystemConfig
```python
# scripts/validate_system_config.py
def validate_system_config():
    # Verificar que no haya claves duplicadas
    duplicates = SystemConfig.objects.values('key').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    if duplicates.exists():
        print("ERROR: Claves duplicadas encontradas")
        for dup in duplicates:
            print(f"  - {dup['key']}: {dup['count']} registros")
        return False
    
    return True
```

### 5.2 Script: Validar StudentNote Enrollment
```python
# scripts/validate_student_note_enrollment.py
def validate_student_note_enrollment():
    # Verificar registros sin enrollment
    orphan_notes = StudentNote.objects.filter(enrollment__isnull=True)
    count = orphan_notes.count()
    
    if count > 0:
        print(f"WARNING: {count} notas sin enrollment")
        print("Opciones:")
        print("  1. Asignar a enrollment existente")
        print("  2. Eliminar registros huérfanos")
        print("  3. Mantener nullable (NO RECOMENDADO)")
        return False, orphan_notes
    
    return True, []
```

### 5.3 Script: Verificar Unique Constraints
```python
# scripts/check_unique_constraints.py
def check_unique_constraints():
    issues = []
    
    # Section: (school_year, academic_grade, parallel)
    duplicates = Section.objects.values(
        'school_year_id', 'academic_grade_id', 'parallel'
    ).annotate(count=Count('id')).filter(count__gt=1)
    
    if duplicates.exists():
        issues.append(("Section", duplicates))
    
    # SubjectAcademicConfig: (subject, academic_grade)
    duplicates = SubjectAcademicConfig.objects.values(
        'subject_id', 'academic_grade_id'
    ).annotate(count=Count('id')).filter(count__gt=1)
    
    if duplicates.exists():
        issues.append(("SubjectAcademicConfig", duplicates))
    
    # TeacherSubjectSection: (user, subject_offering)
    duplicates = TeacherSubjectSection.objects.values(
        'user_id', 'subject_offering_id'
    ).annotate(count=Count('id')).filter(count__gt=1)
    
    if duplicates.exists():
        issues.append(("TeacherSubjectSection", duplicates))
    
    return issues
```

---

## 6. Plan de Rollback

### Estrategia de Reversión

1. **Backups Previos:**
   - Backup completo de la base de datos antes de iniciar
   - Backup de esquema específico por migración

2. **Migraciones Reversibles:**
   - Cada migración individual es reversible con `python manage.py migrate <app> <previous_migration>`

3. **Plan de Contingencia:**

   | Fase Fallida | Acción de Reversión |
   |--------------|---------------------|
   | SystemConfig PK | `python manage.py migrate configuration 0001` |
   | QualitativeScale bridge | `python manage.py migrate grading 0001` |
   | Section unique | `python manage.py migrate institutions 0001` |
   | StudentNote enrollment | `python manage.py migrate grading 0002` |

---

## 7. Checklist de Ejecución

### Pre-ejecución
- [ ] Generar backup completo de la base de datos
- [ ] Ejecutar script de validación de SystemConfig
- [ ] Ejecutar script de validación de StudentNote
- [ ] Ejecutar script de verificación de unique constraints
- [ ] Resolver duplicados encontrados
- [ ] Revisar dependencias de código (repositorios, servicios, serializers)

### Ejecución
- [ ] python manage.py makemigrations configuration --name "add_pk_remove_updated_at"
- [ ] python manage.py migrate configuration
- [ ] python manage.py makemigrations grading --name "create_qualitative_scale_sublevel"
- [ ] python manage.py migrate grading
- [ ] python manage.py makemigrations institutions --name "add_section_unique"
- [ ] python manage.py migrate institutions
- [ ] python manage.py makemigrations academic --name "add_unique_constraints"
- [ ] python manage.py migrate academic
- [ ] python manage.py makemigrations grading --name "make_enrollment_required"
- [ ] python manage.py migrate grading
- [ ] python manage.py makemigrations academic --name "add_parent_period"
- [ ] python manage.py migrate academic

### Post-ejecución
- [ ] Ejecutar tests: `python manage.py test --settings=config.settings.test`
- [ ] Verificar integridad referencial
- [ ] Revisar logs de migración
- [ ] Actualizar documentación de modelos
- [ ] Notificar al equipo de cambios realizados

---

## 8. Impacto en Código Dependiente

### 8.1 Repositorios Afectados

| Repositorio | Cambios Requeridos |
|-------------|-------------------|
| `apps/grading/repositories/student_note_repo.py` | Verificar queries que usan enrollment nullable |
| `apps/configuration/repositories/config_repo.py` | Actualizar acceso a SystemConfig por key |

### 8.2 Servicios Afectados

| Servicio | Cambios Requeridos |
|----------|-------------------|
| `apps/grading/services/note_service.py` | Validar enrollment presente antes de crear nota |
| `apps/configuration/services/config_service.py` | Usar nuevo campo id o mantener acceso por key |

### 8.3 API/Serializers Afectados

| Serializer | Cambios Requeridos |
|------------|-------------------|
| `StudentNoteSerializer` | Remover `required=False` de enrollment |

---

## 9. Estimación de Esfuerzo

| Tarea | Complejidad | Tiempo Estimado |
|-------|------------|-----------------|
| SystemConfig PK migration | Media | 2 horas |
| QualitativeScale bridge table | Baja | 1 hora |
| Unique constraints | Baja | 1 hora |
| StudentNote enrollment | Alta | 3 horas |
| AcademicPeriod parent | Baja | 1 hora |
| Testing y validación | Media | 4 horas |
| **Total** | - | **12 horas** |

---

## 10. Aprobaciones Requeridas

- [ ] Revisión de arquitectura de base de datos
- [ ] Validación de equipo de desarrollo
- [ ] Aprobación de stakeholder de negocio
- [ ] Plan de comunicación a equipos dependientes (frontend, mobile)

---

## 11. Métricas de Éxito

Al finalizar Phase 1:

1. **Integridad Estructural:**
   - 100% de FK críticas con nulabilidad correcta
   - 0 dependencias circulares no resueltas
   - Unique constraints definidos en todas las tablas maestras

2. **Calidad de Datos:**
   - 0 registros huérfanos en StudentNote
   - 0 duplicados en claves naturales
   - 100% de catálogos normalizados

3. **Rendimiento:**
   - Índices únicos activos para consultas frecuentes
   - Query plans optimizados post-migración

4. **Cobertura de Tests:**
   - 100% de modelos con tests unitarios pasando
   - Tests de integridad referencial implementados

---

## 12. Documentación de Referencia

- Modelo ER Actual: `models_er.mmd`
- Documento de Correcciones: `Correcciones.md` - Sección Fase 1
- Configuración Django: `config/settings/base.py`
- URLs del proyecto: `config/urls.py`

---

**Próximo Paso:** Continuar con Fase 2 (Normalización y Depuración) después de validar Phase 1.