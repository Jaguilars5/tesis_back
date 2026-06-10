# Plan de Corrección por Fases — Modelo Relacional
## Sistema de Gestión Académica + Predicción de Deserción (Institución Única, Offline-First)

> Plan ejecutable derivado de la Auditoría Técnica (Versión 2). Backend: Django REST Framework + Clean Architecture (api → services → selectors → repositories → models). Alcance: institución educativa ecuatoriana única, normativa MINEDUC.

> **Versión 2 del plan — escenario de BD nueva.** La base de datos **no tiene datos** y se elimina para arrancar con un esquema limpio. Esto **elimina toda migración de datos, limpieza de datos sucios y respaldos restaurables**. El refactor se aplica directamente sobre los modelos y se regeneran las migraciones desde cero. Cada fase ahora se valida con **pruebas sobre datos de ejemplo (fixtures/seeds)**, no con migración de datos existentes.

> **Cómo leer este plan.** Las fases están ordenadas por **dependencia técnica + criticidad**. Cada fase tiene: estado actual, resultado esperado, pasos, criterios de aceptación y riesgos. No avances a una fase con dependencia marcada hasta cumplir los criterios de aceptación de la anterior.

---

## Resumen de fases

| Fase | Nombre | Criticidad | Bloquea a | Esfuerzo aprox. |
|---|---|---|---|---|
| 0 | Reset de esquema y red de seguridad | — | Todas | 0.25 día |
| 1 | Contrato de auditoría temporal (`updated_at`) | 🔴 | 2, 7 | 0.25 día |
| 2 | Unificación del estado de sincronización | 🔴 | 7 | 0.5 día |
| 3 | Integridad de datos (nulabilidad y constraints) | 🔴 | 7 | 0.25 día |
| 4 | Reconexión del horario (`ClassSchedule` → docente) | 🔴 | — | 0.5 día |
| 5 | Fusión de proyectos en `EvaluationBlock` | 🔴 | — | 1–1.5 días |
| 6 | Refactor de `ConductIncident` | 🟡 | — | 0.5 día |
| 7 | Poda de tablas y simplificación a choices | 🟡 | (depende 1,2,3) | 1 día |
| 8 | `GradingPolicy` y reglas MINEDUC tipadas | 🟡 | — | 0.75 día |
| 9 | Una sola fuente de verdad para promedios | 🟡 | — | 0.5 día |
| 10 | Limpieza analítica y de índices | 🟢 | — | 0.25 día |

> El esfuerzo bajó respecto a la versión anterior porque **no hay migración de datos**: cada cambio de esquema es un `makemigrations` limpio.

> Pendiente transversal: **decisión de proyectos por-materia vs multi-materia** (afecta Fase 5). Resolver antes de iniciar la Fase 5.

---

## Fase 0 — Reset de esquema y red de seguridad

### Estado actual
La BD no tiene datos y se va a eliminar. Las migraciones actuales reflejan el modelo con los problemas de la auditoría. Conviene partir de un estado de migraciones limpio para no arrastrar el historial del modelo viejo.

### Resultado esperado
Un punto de partida limpio: rama de trabajo, migraciones regeneradas desde cero, BD recreada vacía y una suite mínima de pruebas que valide los flujos críticos con datos de ejemplo.

### Pasos a seguir
1. Crear rama `refactor/auditoria-modelo` desde `main`.
2. Eliminar la BD actual (borrar el archivo SQLite o `DROP DATABASE` en SQL Server, según entorno).
3. Borrar los archivos de migración generados de cada app (conservar los `__init__.py` de las carpetas `migrations/`). No tener miedo: no hay datos que preservar.
4. Definir/actualizar un set de **fixtures o seeds** mínimos (un año escolar, un nivel, una materia, una sección, una matrícula, un docente) para poder probar cada fase.
5. Documentar en `CHANGELOG_refactor.md` cada fase aplicada (qué modelo cambió, qué migración).

### Criterios de aceptación
- [ ] Rama creada y aislada de `main`.
- [ ] BD recreada vacía y la app arranca sin errores.
- [ ] `python manage.py makemigrations` y `migrate` corren limpio desde cero.
- [ ] Existe un seed/fixture mínimo que permite ejercitar los flujos 1–7.
- [ ] Suite de pruebas de humo en verde sobre el seed.

### Riesgos
- Borrar migraciones de apps de terceros o el `__init__.py` por error. Solo borrar las migraciones propias del proyecto.

---

## Fase 1 — Contrato de auditoría temporal (`updated_at`) 🔴

### Estado actual
`core.TimeStampedModel` define `updated_at = models.DateTimeField(default=timezone.now)`. El campo **nunca se auto-actualiza** en cada `save()`; queda congelado en el valor de creación. Esto invalida la estrategia offline-first de "última escritura gana" (last-write-wins): dos dispositivos editan el mismo registro y ninguno actualiza `updated_at`, por lo que no se puede determinar la versión más reciente. Es el **riesgo #1 de todo el sistema**.

### Resultado esperado
`created_at` se fija una sola vez al crear; `updated_at` se actualiza automáticamente en cada guardado.

### Pasos a seguir
1. En `TimeStampedModel`, cambiar a:
   - `created_at = models.DateTimeField(auto_now_add=True)`
   - `updated_at = models.DateTimeField(auto_now=True)`
2. Regenerar migraciones (limpio, sin datos que retro-rellenar).
3. Revisar que ningún código setee `updated_at` manualmente esperando que persista (con `auto_now=True`, Django lo sobrescribe en cada save).
4. Verificar que el mixin de sync (`SyncableModel`) usa este `updated_at` corregido como base de comparación de conflictos.

### Criterios de aceptación
- [ ] Al editar y guardar cualquier registro, `updated_at` cambia y `created_at` no.
- [ ] Prueba automatizada: crear → leer `updated_at` → modificar → guardar → confirmar que `updated_at` aumentó.
- [ ] No quedan asignaciones manuales de `updated_at` en servicios/repositories.

### Riesgos
- Mínimos en BD nueva. Solo asegurar que no quede código que dependa de fijar `updated_at` a mano.

### Dependencias
Bloquea la Fase 2 (sync) y la Fase 7 (poda de sync). Hacer primero.

---

## Fase 2 — Unificación del estado de sincronización 🔴

### Estado actual
Hay **doble fuente de verdad** para el estado de sync: el enum `SyncStatusChoices` (TextChoices en `SyncableModel`) **y** una tabla paramétrica `SyncStatus` (módulo `integration`). Además `SyncOperation` es una tabla con 3 valores fijos (CREATE/UPDATE/DELETE) que duplica un enum. `SyncQueue.status`/`operation` apuntan a las tablas, mientras el mixin usa el enum → inconsistencia.

### Resultado esperado
Una única representación del estado y la operación de sync, basada en `TextChoices`. `SyncQueue` y el mixin comparten el mismo vocabulario. Se eliminan las tablas redundantes.

### Pasos a seguir
1. Definir/consolidar `SyncStatusChoices` y crear `SyncOperationChoices` (`CREATE`/`UPDATE`/`DELETE`) como `TextChoices`.
2. Cambiar `SyncQueue.status` y `SyncQueue.operation` de FK a `CharField(choices=...)`.
3. Eliminar del modelo las tablas `SyncStatus` y `SyncOperation`.
4. Ajustar selectors/repositories que filtraban por la FK para que filtren por el código del enum.
5. Regenerar migraciones.

### Criterios de aceptación
- [ ] `SyncQueue` usa `CharField(choices=...)` para `status` y `operation`.
- [ ] No quedan FK ni referencias a `SyncStatus`/`SyncOperation`; las tablas no existen en el esquema.
- [ ] El mixin de sync y la cola usan el mismo vocabulario de estados.
- [ ] Prueba: encolar una operación, procesarla y verificar transición de estado coherente.

### Riesgos
- Referencias residuales al modelo eliminado en código (imports, serializers). Buscar todos los usos antes de borrar.

### Dependencias
Requiere Fase 1 (el conflicto de sync depende de `updated_at` correcto).

---

## Fase 3 — Integridad de datos (nulabilidad y constraints) 🔴

### Estado actual
- `Attendance.attendance_status` y `Attendance.attendance_date` son `null=True` → un registro de asistencia puede existir sin estado ni fecha (sin sentido funcional).
- `StudentNote.evaluative_activity` es `null=True` junto con `unique_together(enrollment, activity)` → la constraint no protege duplicados cuando `activity` es null.
- `StudentRiskFactor`/`StudentFeatureSnapshot`/`StudentRiskScore` tienen `enrollment null=True` marcado como "temporal de migración".

### Resultado esperado
Las columnas obligatorias por dominio nacen `NOT NULL` desde el esquema limpio; las constraints de unicidad protegen realmente; se eliminan las nulabilidades "temporales de migración" que ya no tienen razón de ser.

### Pasos a seguir
1. `Attendance.attendance_status` y `attendance_date` → `NOT NULL`.
2. `StudentNote`: si la nota siempre cuelga de una actividad, poner `evaluative_activity` `NOT NULL`. Si admite nota sin actividad, reemplazar `unique_together` por un `UniqueConstraint` condicional (con `condition`).
3. Quitar el `null=True` "temporal" de `enrollment` en `StudentRiskFactor`, `StudentFeatureSnapshot`, `StudentRiskScore` → `NOT NULL`.
4. Verificar `null=True, blank=True` coherente donde se use `on_delete=SET_NULL`.
5. Regenerar migraciones.

### Criterios de aceptación
- [ ] `Attendance.attendance_status` y `attendance_date` son `NOT NULL` en el esquema.
- [ ] La unicidad de `StudentNote` no se puede violar con duplicados reales (probado con caso límite si `activity` admite null).
- [ ] `enrollment` es `NOT NULL` en las tres tablas analíticas.
- [ ] El seed mínimo respeta las nuevas obligatoriedades sin fallar.

### Riesgos
- Que el seed/fixture intente crear registros sin los campos ahora obligatorios. Actualizar los fixtures junto con el esquema.

### Dependencias
Independiente del resto.

---

## Fase 4 — Reconexión del horario (`ClassSchedule` → docente) 🔴

### Estado actual
`ClassSchedule` se vincula a `SubjectOffering` pero **no a `TeacherSubjectSection`**, así que el horario no sabe qué docente dicta. Además arrastra `classroom` y `building`, datos de espacio físico que el sistema **no gestiona** (decisión 3). La asistencia **no debe** conectarse al horario por FK directa: el horario es estructura recurrente; la asistencia es un evento puntual anclado a `TeacherSubjectSection` + `attendance_date`.

### Resultado esperado
El horario cuelga de la asignación docente-materia-sección y puede derivar la "clase del día". Sin campos de espacio físico. La asistencia permanece desacoplada del horario.

### Pasos a seguir
1. Reemplazar la FK a `SubjectOffering` por `teacher_subject_section = ForeignKey(TeacherSubjectSection, on_delete=CASCADE, related_name="schedules")` (la oferta queda accesible vía `teacher_subject_section.subject_offering`).
2. Eliminar los campos `classroom` y `building`. **No** crear tabla `Classroom` ni campo de aula en `Section`.
3. Cambiar `day_of_week` a `IntegerField(choices=DayOfWeek.choices)` (preparando Fase 7).
4. Ajustar `unique_together` a `(teacher_subject_section, day_of_week, start_time)`.
5. Confirmar que **no** se añade ninguna FK de `Attendance` hacia `ClassSchedule`.
6. Regenerar migraciones.

### Criterios de aceptación
- [ ] `ClassSchedule` tiene FK a `TeacherSubjectSection` y ya no a `SubjectOffering` directamente.
- [ ] Los campos `classroom`/`building` ya no existen; no se creó entidad de aula.
- [ ] Se puede derivar el docente de cualquier horario sin joins externos adicionales.
- [ ] No existe FK directa `Attendance` → `ClassSchedule`.
- [ ] La unicidad impide dos horarios solapados para la misma asignación, día y hora de inicio.

### Riesgos
- Código que navegaba `ClassSchedule.subject_offering` directamente: actualizarlo a `class_schedule.teacher_subject_section.subject_offering`.

### Dependencias
Independiente. Puede correr en paralelo a las fases 1–3.

---

## Fase 5 — Fusión de proyectos en `EvaluationBlock` 🔴

### Estado actual
`InterdisciplinaryProject`, `SubjectProject` y `ProjectNote` forman un **subsistema paralelo** que no se integra con el pipeline `EvaluationBlock → BlockComponent → EvaluativeActivity → StudentNote → PeriodGradeSummary`. Las notas de proyecto **no ponderan** en la nota del período (Flujo 2.5). Además `EvaluativeActivity.is_interdisciplinary_project` es un booleano huérfano sin FK.

### Resultado esperado
El proyecto es **un bloque de evaluación más**: un `EvaluationBlock` con `evaluation_type = PROJECT` y dos `BlockComponent` ("Producto", "Presentación"). Las calificaciones se vuelven `StudentNote` normales que entran automáticamente al `PeriodGradeSummary`. Desaparecen las tres tablas y el booleano huérfano.

### Decisión pendiente (resolver antes de empezar)
**¿Los proyectos se califican dentro de UNA materia o cruzan VARIAS?**
- **Por materia** → fusión total, el bloque cuelga de un único `SubjectOffering`. Nada extra.
- **Multi-materia (interdisciplinario real)** → añadir `linked_offerings = ManyToManyField(SubjectOffering)` al `EvaluationBlock` (reemplaza la función puente de `SubjectProject`); si se necesita docente responsable por materia, un `through` ligero sobre ese M2M.

### Pasos a seguir
1. Resolver la decisión por-materia/multi-materia.
2. Extender `EvaluationType`/`evaluation_type` para soportar `PROJECT`.
3. Eliminar del modelo `InterdisciplinaryProject`, `SubjectProject`, `ProjectNote` y el campo `EvaluativeActivity.is_interdisciplinary_project`.
4. Si es multi-materia, añadir `linked_offerings = ManyToManyField(SubjectOffering)` a `EvaluationBlock`.
5. Trasladar las rúbricas (`product_max_score`/`presentation_max_score`) a `max_score` de los dos `BlockComponent` o a la actividad.
6. Actualizar fixtures/seeds y los servicios de creación de proyectos para usar el nuevo flujo.
7. Regenerar migraciones.

### Criterios de aceptación
- [ ] No existen las tablas `InterdisciplinaryProject`/`SubjectProject`/`ProjectNote`; el booleano huérfano fue eliminado.
- [ ] Un proyecto se crea como `EvaluationBlock` tipo PROJECT con sus dos componentes.
- [ ] La nota de un proyecto **aparece reflejada** en el `PeriodGradeSummary` del estudiante (probado con el seed).
- [ ] Si es multi-materia: el M2M `linked_offerings` enlaza el bloque con todas las materias participantes.
- [ ] La suma ponderada del período (Flujo 2.5) cuadra incluyendo proyectos.

### Riesgos
- Si la decisión por-materia/multi-materia cambia después de implementar, hay retrabajo de esquema. Por eso es bloqueante resolverla antes.

### Dependencias
Independiente del resto, pero requiere la decisión transversal resuelta.

---

## Fase 6 — Refactor de `ConductIncident` 🟡

### Estado actual
`ConductIncident` ejecuta `get_or_create` dentro del `__init__` / setter de la property `category`. Instanciar el objeto dispara **escrituras en la base de datos**, lo cual es peligroso en migraciones, tests y escenarios offline (efectos secundarios inesperados, escrituras fuera de transacción controlada).

### Resultado esperado
Crear una instancia de `ConductIncident` no produce efectos secundarios en BD. La relación con el tipo de incidente se maneja con una FK directa explícita.

### Pasos a seguir
1. Eliminar la lógica `get_or_create` del `__init__` y del setter de `category`.
2. Usar la FK `incident_type` directamente; la creación/selección del tipo se hace en la capa de servicios, no en el modelo.
3. Migrar cualquier código que dependiera del comportamiento mágico de la property hacia la capa de servicios (Clean Architecture).

### Criterios de aceptación
- [ ] Instanciar `ConductIncident(...)` en memoria no genera ninguna escritura en BD.
- [ ] La asignación de tipo de incidente pasa por la FK `incident_type` explícita.
- [ ] Las pruebas de creación de incidentes pasan sin efectos colaterales.

### Riesgos
- Código existente que asumía el atajo de la property. Buscar todos los usos antes de eliminar.

### Dependencias
Independiente.

---

## Fase 7 — Poda de tablas y simplificación a choices 🟡

### Estado actual
~60 tablas para una sola institución. Varias paramétricas anémicas (`code/name/description/is_active`) modelan conjuntos cerrados y estables que no se editan desde la UI. Infraestructura prematura sin consumidor (`SyncSchemaVersion`, `DashboardMetric`).

### Resultado esperado
Modelo reducido (~45 tablas), con catálogos cerrados convertidos a `TextChoices`/`IntegerChoices` y eliminación de infraestructura sin uso. Se conservan los catálogos legítimos (con reglas o editables).

### Pasos a seguir
1. **Eliminar del modelo**: `DashboardMetric`, `SyncSchemaVersion` (además de `SyncStatus`/`SyncOperation` ya tratadas en Fase 2). Confirmar que ningún flujo (1–7) los consume.
2. **Simplificar a choices**: `DayOfWeek`, `PromotionStatus`, `EnrollmentStatus`, `RecoveryProcessStatus`, `UrgencyLevel`, `AlertType`. Reemplazar las FK que las usaban por `CharField`/`IntegerField(choices=...)`.
3. **Quitar campo intruso**: eliminar `AttendanceStatus.tipo` (POSITIVO/NEGATIVO) — es vocabulario de conducta, no de asistencia. Si se necesita para KPIs, derivar o usar un flag claro como `counts_as_absence`.
4. **Evaluar**: `GradeType` y `ComponentIndicator` — eliminar `GradeType` salvo que cumpla un rol no cubierto por `StudentNote.grading_mode`; colapsar `ComponentIndicator` si en la práctica los docentes crean actividades directamente en el componente.
5. **Mantener** (no tocar): `Severity`, `RecoveryProcessType`, `QualitativeScale`, `RiskFactor`, `WithdrawalReason`, `ResidentialZone`, `SpecialNeedsType`, `Kinship`, `DocumentType`, `AbsenceType`, `IncidentType`, `SocioemotionalArea/Skill`, `DevelopmentLevel`.
6. Actualizar fixtures/seeds y regenerar migraciones.

### Criterios de aceptación
- [ ] Las tablas eliminadas no tienen FK entrantes y no existen en el esquema.
- [ ] Cada catálogo simplificado fue reemplazado por un enum y las FK que lo usaban ahora son campos con choices.
- [ ] `AttendanceStatus.tipo` eliminado; ningún flujo lo referencia.
- [ ] Decisión registrada (mantener o eliminar) para `GradeType` y `ComponentIndicator`, con justificación.
- [ ] La app arranca y los flujos 1–7 funcionan tras la poda (probado con el seed).

### Riesgos
- Simplificar a choices un catálogo que sí se edita desde la UI rompe la gestión. Criterio: si la secretaría edita el catálogo o este tiene atributos de negocio, **se mantiene como tabla**.

### Dependencias
La parte de sync (`SyncStatus`/`SyncOperation`) depende de las Fases 1 y 2. El resto es independiente.

---

## Fase 8 — `GradingPolicy` y reglas MINEDUC tipadas 🟡

### Estado actual
`SystemConfig` es un almacén clave/valor genérico (anti-patrón EAV) sin tipado ni consumidor identificado. No existe ninguna tabla tipada que almacene las ponderaciones del Ministerio por período (40/50/10, 70/30 formativo/sumativo, nota mínima). El Flujo 1 (configuración de ponderaciones) no tiene soporte estructurado.

### Resultado esperado
Las reglas de negocio MINEDUC viven en una tabla tipada `GradingPolicy` con columnas reales y FK a `SchoolYear`/`AcademicLevel`/`PeriodType`. Las constantes técnicas pasan a settings/entorno. `SystemConfig` se elimina.

### Pasos a seguir
1. Crear `GradingPolicy` (ver §12.2 de la auditoría): `school_year`, `academic_level`, `period_type`, `period_weight`, `formative_weight`, `summative_weight`, `grading_mode`, `min_passing_grade`, `is_active`, con `unique_together(school_year, academic_level, period_type)`.
2. Mover constantes técnicas (timeouts, versiones, flags) a settings/variables de entorno.
3. Conectar la validación de pesos de `EvaluationBlock`/`BlockComponent` contra `GradingPolicy` (los pesos deben sumar lo que define la política).
4. Eliminar `SystemConfig` del modelo.
5. Añadir al seed las filas de `GradingPolicy` para los niveles/períodos de prueba (ej. 40/50/10 y 70/30).
6. Regenerar migraciones.

### Criterios de aceptación
- [ ] `GradingPolicy` creada y poblada en el seed con ponderaciones reales por período/nivel.
- [ ] El Flujo 1 (configurar 40/50/10 y 70/30) se resuelve leyendo/escribiendo `GradingPolicy`, no strings.
- [ ] La validación de pesos de bloques/componentes referencia la política.
- [ ] `SystemConfig` eliminada; las constantes técnicas viven en settings.
- [ ] Prueba: cambiar una ponderación en `GradingPolicy` afecta el cálculo del período correspondiente.

### Riesgos
- Que queden referencias en código a claves de `SystemConfig`. Buscar y reemplazar por `GradingPolicy`/settings antes de eliminar.

### Dependencias
Independiente. Conviene hacerla cerca de la Fase 5 (ambas tocan el cálculo de notas del período).

---

## Fase 9 — Una sola fuente de verdad para promedios 🟡

### Estado actual
Tres tablas guardan "el promedio del período" sin jerarquía clara: `PeriodGradeSummary` (`formative_avg`, `summative_avg`, `final_avg_truncated`), `LearningReport` (`formative_avg`, `summative_avg`, `final_avg`, `attendance_rate`) y `StudentFeatureSnapshot`. `LearningReport` recopia lo que ya está en `PeriodGradeSummary`; riesgo de inconsistencia.

### Resultado esperado
`PeriodGradeSummary` es la **única fuente de verdad** del promedio del período (caché explícita con `calculated_at`). `LearningReport` referencia/deriva en vez de recopiar. `StudentFeatureSnapshot` se mantiene como congelado intencional para IA (documentado).

### Pasos a seguir
1. Confirmar `PeriodGradeSummary` como fuente única; marcar sus columnas derivadas como caché con `calculated_at` y poblarlas por evento (al guardar nota) o por job.
2. En `LearningReport`, convertir los promedios en propiedades calculadas o FK a `PeriodGradeSummary` (+ `BehaviorEvaluation` para la conducta del informe, en lugar de la escala suelta `behavior_scale`). Conservar solo lo propio del informe: observaciones, recomendaciones, aprobaciones, `is_final`.
3. Documentar que `StudentFeatureSnapshot` congela el estado a propósito (es correcto para IA, no es un error de 3FN).
4. Regenerar migraciones.

### Criterios de aceptación
- [ ] `LearningReport` ya no almacena promedios propios; los obtiene de `PeriodGradeSummary`/`BehaviorEvaluation`.
- [ ] `PeriodGradeSummary` tiene `calculated_at` poblado y un mecanismo (evento o job) que lo mantiene.
- [ ] No hay discrepancia entre el promedio del informe y el de `PeriodGradeSummary` (probado con el seed).
- [ ] Decisión sobre `StudentFeatureSnapshot` documentada como desnormalización intencional.

### Riesgos
- Si más adelante (ya en producción con datos) se requiere trazabilidad de "lo que se comunicó al representante en la fecha X", habrá que versionar o snapshotear el informe. En BD nueva no es problema ahora, pero déjalo anotado como decisión de diseño futura.

### Dependencias
Conviene después de Fase 5 (los proyectos ya entran al summary) y Fase 8 (ponderaciones tipadas).

---

## Fase 10 — Limpieza analítica y de índices 🟢

### Estado actual
Faltan índices en algunas tablas de consulta frecuente: `BehaviorEvaluation`/`SkillEvaluation` por `enrollment` directo. (Los índices de `Attendance`, `StudentNote`, `EvaluativeActivity`, `PeriodGradeSummary`, `SyncQueue` ya están bien.)

### Resultado esperado
Consultas de los Flujos 5/6 (informes y analítica) eficientes, con índices compuestos donde falten. Sin índices muertos sobre tablas eliminadas.

### Pasos a seguir
1. Añadir índices compuestos por `(enrollment, academic_period)` en `BehaviorEvaluation` y `SkillEvaluation` si las consultas reales los necesitan.
2. Confirmar que ningún `Meta.indexes` quedó apuntando a tablas/campos removidos en fases previas (proyectos, dashboard, sync). En BD nueva esto se valida porque `makemigrations` fallaría si referencia algo inexistente.
3. Verificar que `StudentFeatureSnapshot` mantiene su rol de vector plano por `(matrícula, período)` para inferencia sin joins.
4. Regenerar migraciones finales.

### Criterios de aceptación
- [ ] Los `Meta.indexes` definidos compilan y aplican sin error.
- [ ] No quedan índices que referencien tablas eliminadas.
- [ ] Las consultas de informe por estudiante/período tienen índice de apoyo.

### Riesgos
- Sobre-indexar penaliza escrituras (importante en offline-first con sync). Añadir solo los índices que las consultas reales justifican.

### Dependencias
Última fase: depende de que la poda (Fase 7) y las fusiones (Fase 5) ya estén aplicadas.

---

## Secuenciación recomendada

```
Fase 0 (reset de esquema)
   │
   ├──► Fase 1 (updated_at) ──► Fase 2 (sync) ──┐
   │                                            │
   ├──► Fase 3 (integridad) ────────────────────┤
   │                                            ├──► Fase 7 (poda) ──► Fase 10 (índices)
   ├──► Fase 4 (horario)  ───────────────────────┘
   │
   ├──► Fase 5 (proyectos)*  ──┐
   │   (*requiere decisión)    ├──► Fase 9 (fuente única de promedios)
   ├──► Fase 8 (GradingPolicy)─┘
   │
   └──► Fase 6 (ConductIncident)  [independiente, en cualquier momento]
```

- **Camino crítico**: 0 → 1 → 2 → 7. Es la columna vertebral del offline-first.
- **Paralelizable**: Fases 4, 5, 6 y 8 pueden avanzar en paralelo al camino crítico (distintos módulos).
- **Bloqueante de negocio**: la decisión por-materia/multi-materia debe resolverse antes de iniciar la Fase 5.
- **Atajo posible**: como no hay datos, puedes aplicar varias fases de un mismo módulo juntas y hacer **un solo `makemigrations` por módulo** al final, en lugar de uno por fase. Útil si prefieres velocidad sobre granularidad del historial de migraciones.

---

## Checklist global de cierre

- [ ] BD recreada limpia; `makemigrations`/`migrate` corren desde cero sin error.
- [ ] El modelo bajó de ~60 a ~45 tablas.
- [ ] `updated_at` se auto-actualiza en todo el modelo (offline-first salvado).
- [ ] Estado de sync unificado en un solo enum; sin tablas redundantes.
- [ ] `ClassSchedule` conoce al docente; sin campos de espacio físico; asistencia desacoplada del horario.
- [ ] Proyectos integrados en el pipeline de evaluación; sus notas ponderan en el período.
- [ ] Reglas MINEDUC tipadas en `GradingPolicy`; `SystemConfig` eliminada.
- [ ] Un solo "promedio del período" como fuente de verdad.
- [ ] `ConductIncident` sin efectos secundarios en el constructor.
- [ ] Seed/fixture mínimo ejercita los flujos 1–7 en verde.
- [ ] `CHANGELOG_refactor.md` con cada cambio de modelo registrado.

---

> Fuente: Auditoría Técnica del Modelo Relacional, Versión 2 (este mismo proyecto). Cada fase es trazable a las secciones 7–12 de ese documento. Plan adaptado a escenario de **base de datos nueva sin datos**: sin migración de datos, validación por fixtures/seeds.
