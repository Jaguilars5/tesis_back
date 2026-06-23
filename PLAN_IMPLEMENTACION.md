# Plan de Implementación por Fases — Correcciones y Actualizaciones

> **Base:** `AUDITORIA_MODELOS.md` (secciones 5, 6 y 9).
> **Ámbito:** backend `apps/analytics` (+ `attendance`, `grading`, `students`, `people`) y
> frontend `web-front`.
> **Fecha:** 2026-06-23
> **Estado global:** Fases 0, 1, 2, 3, 4 y 5 completadas (2026-06-23).

---

## 0. Principios y orden de ejecución

- **Orientado a riesgo→valor:** primero se arregla lo que invalida el score (Fase 1), luego se
  consolidan datos (Fase 2), se limpia el ruido (Fase 3), se enriquece (Fase 4) y por último se
  habilita la configuración institucional (Fase 5).
- **Compatibilidad hacia atrás:** cada fase mantiene el sistema funcionando (fallback por reglas
  siempre disponible).
- **Trazabilidad:** todo cambio en el cálculo incrementa `model_version` para reproducibilidad.
- **Pruebas primero:** usar el runner de Django con `--settings=config.settings.test`.

### Dependencias entre fases

```
Fase 0 (baseline)
   └─> Fase 1 (contrato de features / tren-inferencia)  [CRÍTICA]
          ├─> Fase 2 (unificación de fuentes)
          │       └─> Fase 3 (limpieza de features muertas)
          │               └─> Fase 4 (enriquecimiento: City, SpecialNeedsType, WithdrawalReason)
          └─> Fase 5 (motor de reglas configurable)  [puede ir en paralelo tras Fase 1]
```

---

## Fase 0 — Baseline y red de seguridad ✅ COMPLETADA (2026-06-23)

**Objetivo:** congelar el comportamiento actual y poder medir regresiones.

**Tareas**
- [x] Documentar el score actual de un conjunto de estudiantes de prueba (snapshot dorado).
- [x] Verificar/crear tests de `calculate_academic_risk`, `_risk_level`, `_fallback_risk_score`,
  `feature_builder` y `early_alert_service` que fijen el comportamiento vigente.
- [x] Confirmar si existe `risk_model.joblib` (confirmado: **no existe** → todo corre por fallback).

**Criterios de aceptación**
- [x] Suite verde con `python manage.py test apps.analytics --settings=config.settings.test`
  (**122 tests OK**, incluyendo 24 nuevos de baseline).
- [x] Conjunto de referencia de scores guardado para comparación.

**Entregables**
- `apps/analytics/tests/baseline_scores.json` — snapshot dorado (5 perfiles de referencia con
  nivel y puntaje esperados; versión de modelo `rules-fallback-v1`).
- `apps/analytics/tests/test_baseline_phase0.py` — red de seguridad que congela:
  ausencia del artefacto ML, `WEIGHTS`, umbrales de `_risk_level`, fórmula y pisos/topes de
  `_fallback_risk_score`, salida extremo a extremo de `calculate_academic_risk` contra el
  baseline dorado, y las reglas de `EarlyAlertService.evaluate_student`.

**Esfuerzo:** 0.5 día · **Riesgo:** bajo.

---

## Fase 1 — Corregir el desajuste tren/inferencia (CRÍTICA) ✅ COMPLETADA (2026-06-23) · Auditoría §6.1, §6.5

**Objetivo:** que `FEATURE_COLUMNS` (entrenamiento) y `_feature_vector` (inferencia) compartan
**un único contrato de features** (mismos nombres, mismo orden), para que el ML pueda puntuar.

**Tareas (backend)**
- [x] Definir una **única fuente de verdad** de features (`apps/analytics/ml/features.py`
  con la lista canónica `FEATURE_COLUMNS` + mappers) consumida tanto por `train_model.py`
  como por `tasks._predict_ml_score`/`_feature_vector`.
- [x] Reescribir `_feature_vector` para emitir exactamente las columnas entrenadas (16),
  alineando el snapshot crudo y las métricas de persistencia.
- [x] Incluir en el vector los campos hoy inertes pero ya calculados (§6.5): `is_repeat`,
  `age_grade_gap`, `prev_period_avg_grade`, `family_notified_ratio`,
  `consecutive_absences_max`, `has_special_needs` (todos en el contrato canónico).
- [x] Manejo explícito de "modelo ausente / mismatch": logs `[ML][FALLBACK-INTENCIONAL]` vs
  `[ML][ERROR]`; validación de columnas (`columns_match`) **antes** de `predict`.
- [x] Versionar el artefacto (`MODEL_VERSION_SKLEARN` → `sklearn-joblib-v2`). El reentrenamiento
  real (`python manage.py train_risk_model`) queda pendiente de datos suficientes (≥10 muestras).

**Archivos afectados**
- `apps/analytics/ml/features.py` (NUEVO — fuente única), `apps/analytics/ml/train_model.py`
  (consume el contrato + ruta configurable + imports perezosos),
  `apps/analytics/tasks.py` (`_feature_vector`, `_predict_ml_score`, `_prediction_input`,
  `calculate_academic_risk(snapshot, metrics)`),
  `apps/analytics/services/feature_builder.py` (`build_persistence_metrics` ahora completa
  `justified_absences`, `unjustified_absences`, `severe_incidents_count`).

**Criterios de aceptación**
- [x] Con un modelo entrenado presente (columnas coincidentes), `_predict_ml_score` retorna un
  score **sin** caer a fallback (`test_phase1_feature_contract`; tests con sklearn/joblib se
  ejecutan en el entorno de despliegue, se omiten donde faltan esas libs).
- [x] Test que falla si las columnas de entrenamiento e inferencia divergen
  (`Phase1ColumnContractTest`, corre sin dependencias de ML).
- [x] Logs distinguen "fallback intencional" de "error".

**Entregables**
- `apps/analytics/ml/features.py` y `apps/analytics/tests/test_phase1_feature_contract.py`.

**Esfuerzo:** 1.5–2 días · **Riesgo:** medio (cambia el score productivo → comparar vs baseline).
**Nota de baseline:** sin artefacto ML, el sistema sigue 100% en fallback de reglas; el snapshot
dorado de Fase 0 permanece verde (`model_version=rules-fallback-v1`).

---

## Fase 2 — Unificar fuentes de datos · Auditoría §6.3, §6.4 — ✅ COMPLETADA (2026-06-23)

**Objetivo:** una sola definición canónica para "asistencia" y para "materia reprobada".

**Tareas (backend)**
- [x] **Asistencia (§6.3):** taxonomía canónica elegida = `attendance_status.code` (`P/J/A/T`),
  por ser el campo requerido (PROTECT, no nulo) y el ya usado por `feature_builder`.
  `AttendanceRepository.get_absences_summary` (consumido por `early_alert_service`) ahora
  agrega por `attendance_status.code` con el mapeo `J→justified`, `A→unjustified`, `T→late`,
  `P→present`. `absence_type` queda **deprecado** como fuente de cálculo (se documenta en el
  docstring del repositorio).
- [x] **Reprobado (§6.4):** fuente única = `PeriodGradeSummary.is_failing`, vía el nuevo método
  `PeriodGradeSummaryRepository.count_failing(enrollment_id, period_id)`, consumido por **ambos**
  `feature_builder` (riesgo) y `early_alert_service` (alertas). `feature_builder` dejó de
  recalcular reprobados desde `StudentNote` (se eliminó `_count_failing_subjects(notes)` y la
  constante `PASSING_GRADE`). La sincronía la garantiza el signal de grading existente.
- [x] Bugfix colateral: `early_alert_service` llamaba a `get_severe_by_enrollment(severity_threshold=4)`,
  kwarg inexistente que reventaba cualquier ejecución real de la regla de conducta; corregido a
  la firma real del repositorio.

**Archivos afectados**
- `apps/attendance/repositories/attendance_repository.py` (taxonomía canónica + clave `present`).
- `apps/grading/repositories/period_grade_summary_repository.py` (nuevo `count_failing`).
- `apps/analytics/services/feature_builder.py` (reprobados desde `PeriodGradeSummary`).
- `apps/analytics/services/early_alert_service.py` (reprobados período-acotados + fix de conducta).
- `apps/attendance/tests/test_repositories.py` (fixture alineada a la taxonomía canónica).
- `apps/analytics/tests/test_baseline_phase0.py` (mock `get_by_enrollment` → `count_failing`).

**Entregables**
- `apps/analytics/tests/test_phase2_unification.py` — tests de equivalencia: taxonomía de
  asistencia (summary vs feature_builder), `absence_type` ya no decide el conteo, mismo número
  de reprobados en `feature_builder` y `early_alert_service`, y acotamiento por período.

**Criterios de aceptación**
- [x] `feature_builder` y `early_alert_service` reportan el mismo número de reprobados para el
  mismo estudiante/periodo (ambos usan `count_failing`).
- [x] Tests de equivalencia de taxonomía de asistencia (verde).

**Validación:** suites `apps.analytics`, `apps.attendance` y `apps.grading` en verde
(223 tests, 3 skipped por dependencias ML opcionales).

**Esfuerzo:** 1 día · **Riesgo:** medio · **Depende de:** Fase 1.

---

## Fase 3 — Limpieza de features muertas · Auditoría §6.2, §6.5 — ✅ COMPLETADA (2026-06-23)

**Objetivo:** eliminar ruido fijo y decidir el destino de campos inertes.

**Tareas (backend)**
- [x] **`tareas_entregadas` / `tareas_pendientes` (§6.2):** **eliminadas** del snapshot
  (`feature_builder._build_grades`) y de sus validaciones. No estaban persistidas ni en
  `FEATURE_COLUMNS`; eran ruido constante en `0`. **Deuda futura registrada:** si se
  implementa un modelo de entregas, reintroducirlas como features reales.
- [x] **Campos §6.5 — auditoría de huérfanos:** se detectó que `active_alerts` era un campo
  **huérfano** (persistido en `StudentFeatureSnapshot`, escrito siempre `0` por el builder real,
  **no** en `FEATURE_COLUMNS` ni en inferencia; el dashboard cuenta alertas activas aparte vía
  `EarlyAlert`). Se **eliminó** la columna (migración `0004`), el `setdefault` del repositorio y
  sus referencias en seeds/tests. El resto de campos §6.5 (`is_repeat`, `age_grade_gap`,
  `prev_period_avg_grade`, `has_special_needs`) quedaron confirmados como vivos (integrados en
  Fase 1).

**Archivos afectados**
- `apps/analytics/services/feature_builder.py` (quita `tareas_*` del dict y validaciones).
- `apps/analytics/models/student_feature_snapshot.py` (elimina `active_alerts`).
- `apps/analytics/migrations/0004_remove_studentfeaturesnapshot_active_alerts.py` (nueva).
- `apps/analytics/repositories/analytics_repo.py` (quita `setdefault("active_alerts", 0)`).
- `apps/core/management/commands/seed_test_data.py` (quita `active_alerts`).
- `apps/analytics/tests/test_risk_model.py`, `tests/test_repositories.py` (fixtures actualizadas).

**Entregables**
- `apps/analytics/tests/test_phase3_dead_features.py` — invariantes: `_build_grades` no emite
  `tareas_*`; **no quedan columnas huérfanas** (`{persistidas} ⊆ FEATURE_COLUMNS` y viceversa);
  `active_alerts` ya no existe en el modelo.

**Criterios de aceptación**
- [x] No quedan features con valor constante `0` por diseño.
- [x] Todo campo persistido en `StudentFeatureSnapshot` se usa en entrenamiento **o** inferencia
  (test invariante `Phase3NoOrphanColumnsTest`).

**Validación:** suites `apps.analytics`, `apps.attendance`, `apps.grading` en verde
(227 tests, 3 skipped por dependencias ML opcionales).

**Esfuerzo:** 0.5 día · **Riesgo:** bajo · **Depende de:** Fase 1.

---

## Fase 4 — Enriquecimiento del análisis · Auditoría §5 (F) — ✅ COMPLETADA (2026-06-23)

**Objetivo:** incorporar variables de segmentación con valor para deserción.

**Decisión de diseño (importante):** `City`, `SpecialNeedsType` y `WithdrawalReason` se modelan
como **dimensiones analíticas/segmentación** (FK persistidas en el snapshot), **no** como
features numéricas del modelo ML, porque:
- `City` es de **alta cardinalidad** (codificarla como ordinal/one-hot degrada el contrato numérico).
- `WithdrawalReason` es una **variable de resultado** (solo se conoce tras el retiro) → su uso como
  feature sería **fuga de información** (target leakage).
- El tipo de NEE ya está representado para el modelo por el booleano `has_special_needs`; el **tipo**
  aporta valor sobre todo para **segmentar** (qué tipo deserta más), que es un uso de dashboard.

Por tanto el contrato numérico `FEATURE_COLUMNS` **permanece sin cambios** y **no requiere
reentrenar** el modelo. La coherencia tren/inferencia se mantiene (el vector numérico no cambió);
las nuevas dimensiones son coherentes porque se persisten igual y el dashboard las lee del snapshot
o de `Enrollment`.

**Tareas (backend)**
- [x] **`people.City` (ciudad de origen):** expuesta en `feature_builder.build_persistence_metrics`
  (`city_id` desde `student.user.person.city`), nueva columna FK `city` en `StudentFeatureSnapshot`,
  y segmentación de **riesgo por ciudad** + **índice de deserción por ciudad** en el dashboard.
- [x] **`students.SpecialNeedsType`:** además de `has_special_needs`, se persiste el **tipo**
  (`special_needs_type`) y el dashboard agrupa **riesgo por tipo de NEE**.
- [x] **`students.WithdrawalReason`:** persistido como `withdrawal_reason` y promovido a **reporte
  analítico** (`get_withdrawal_reasons`) desde `Enrollment`.
- [x] Migración `0005` + actualización de `seed_test_data` (set de city/NEE/motivo en el snapshot).
  **Reentrenamiento NO requerido** (ver decisión de diseño: el contrato numérico no cambió).

**Archivos afectados**
- `apps/analytics/models/student_feature_snapshot.py` (FKs `city`, `special_needs_type`, `withdrawal_reason`).
- `apps/analytics/migrations/0005_studentfeaturesnapshot_city_and_more.py` (nueva).
- `apps/analytics/services/feature_builder.py` (`city_id`/`special_needs_type_id`/`withdrawal_reason_id`).
- `apps/analytics/repositories/analytics_repo.py` (passthrough — sin cambios; los `*_id` fluyen por `defaults`).
- `apps/analytics/services/dashboard_service.py` (4 métodos nuevos de segmentación/reporte).
- `apps/analytics/api/views.py` (acciones `risk_by_city`, `risk_by_special_needs`, `dropout_by_city`, `withdrawal_reasons` + permisos).
- `apps/core/management/commands/seed_test_data.py` (pobla las dimensiones).
- `apps/analytics/tests/test_phase3_dead_features.py` (excluye `ANALYTICAL_DIMENSION_FIELDS` del invariante).

**Entregables**
- `apps/analytics/tests/test_phase4_enrichment.py` — `build_persistence_metrics` expone las
  dimensiones, el snapshot las persiste, y el dashboard agrupa riesgo por ciudad y por tipo de NEE,
  calcula deserción por ciudad y reporta motivos de retiro.

**Criterios de aceptación**
- [x] Dashboard puede agrupar deserción/riesgo por ciudad y por tipo de necesidad especial.
- [x] Dimensiones nuevas presentes y coherentes en entrenamiento e inferencia (contrato numérico
  intacto; dimensiones persistidas de forma consistente).

**Validación:** suites `apps.analytics`, `apps.attendance`, `apps.grading` en verde
(233 tests, 3 skipped por dependencias ML opcionales).

**Esfuerzo:** 2–3 días · **Riesgo:** medio · **Depende de:** Fases 1–3.

---

## Fase 5 ✅ — Motor de reglas configurable desde el frontend · Auditoría §9

**Estado:** Completada (2026-06-23).

**Objetivo:** permitir a la institución ajustar **pesos + umbrales** con parámetros seguros.

**Implementado:**
- Backend: modelo `RiskScoringConfig` (singleton), migración `0006`, repositorio
  `RiskScoringConfigRepository` (`get_or_create_singleton`), servicio
  `RiskScoringConfigService.get_effective()` con `EffectiveScoringConfig` + presets
  (Conservador/Equilibrado/Estricto), `tasks.py` lee pesos/umbrales de la config,
  `RiskScoringConfigSerializer` con validación (suma 100%, rangos 10–60%, dominios,
  coherencia rojo<amarillo), `RiskScoringConfigViewSet` (GET / `update_config` /
  `apply_preset`), permisos `view/update_scoring_config` (DIRECTOR/RECTOR), comando
  `seed_scoring_config`, y `model_version` que refleja la config aplicada.
- Frontend (`web-front`): módulo flat `analytics/scoring-config` (`*.types/constants/service/
  slice/controller/utils` + `ScoringConfigPage`), reducer registrado en
  `analytics.scoringConfig` y ruta `/analytics/scoring-config`.
- Tests: `apps/analytics/tests/test_phase5_configurable_rules.py` (169 tests de analytics OK).

**Decisiones tomadas (§9.5):** alcance **global** · motor **ambos** (selector `engine`) ·
configurable **pesos + umbrales del semáforo**.

### 5a. Backend
- Modelo `RiskScoringConfig` (singleton global): `engine` (`ML`|`reglas`),
  `weight_conducta/asistencia/calificaciones`, y umbrales del semáforo
  (cortes de asistencia, promedio y faltas graves para rojo/amarillo).
- Migración + **seed con los valores actuales** como preset por defecto + presets
  "Conservador / Equilibrado / Estricto".
- Repositorio + servicio de lectura; `tasks.py` (`WEIGHTS`, `_risk_level`,
  `_*_level`) leen de la config en vez de constantes.
- **Validadores** (clave para "parámetros seguros"): pesos **suman 100%**, rangos acotados
  (p. ej. peso `10%–60%`), coherencia de umbrales (rojo `<` amarillo `<` verde), dominios
  (asistencia 0–100, notas 0–10).
- ViewSet GET/PATCH con permisos (patrón del repo) + `model_version` refleja la config aplicada.

### 5b. Frontend (`web-front`, patrón flat)
- Módulo nuevo: `*.types.ts`, `*.constants.ts`, `*.service.ts`, `*.slice.ts`,
  `*.controller.ts`, `*.utils.ts` (Yup: suma 100%, rangos), `ConfigPage.tsx`.
- UI: sliders de pesos + inputs de umbrales + selector de motor + botones de preset.
- Registrar reducer y ruta según convenciones del `AGENTS.md` del front.

**Criterios de aceptación**
- Cambiar pesos/umbrales desde el front altera el score **y** la clasificación (por incluir
  umbrales) en el motor de reglas; con `engine=ML` se ignoran (documentado).
- Backend rechaza configuraciones inválidas (suma ≠ 100%, fuera de rango).

**Esfuerzo:** backend ~1–2 días + frontend ~1–2 días · **Riesgo:** medio ·
**Depende de:** Fase 1 (puede iniciar en paralelo tras Fase 1).

---

## Resumen de fases

| Fase | Tema | Auditoría | Esfuerzo | Riesgo | Depende de |
|:----:|------|:---------:|:--------:|:------:|:----------:|
| 0 ✅ | Baseline y tests | — | 0.5 d | Bajo | — |
| 1 ✅ | Tren/inferencia (CRÍTICA) | §6.1, §6.5 | 1.5–2 d | Medio | 0 |
| 2 ✅ | Unificar fuentes | §6.3, §6.4 | 1 d | Medio | 1 |
| 3 ✅ | Limpieza features muertas | §6.2, §6.5 | 0.5 d | Bajo | 1 |
| 4 ✅ | Enriquecimiento (City, etc.) | §5 (F) | 2–3 d | Medio | 1–3 |
| 5 ✅ | Reglas configurables | §9 | 2–4 d | Medio | 1 |

**Total estimado:** ~8–11 días de desarrollo.

---

## Riesgos transversales

- **Reproducibilidad histórica:** al cambiar el cálculo (Fases 1, 4, 5), decidir si los scores
  pasados se **congelan** (con su `model_version`) o se **recalculan**. Recomendado: congelar.
- **Reentrenamiento:** Fases 1 y 4 cambian el set de features → requieren reentrenar el modelo.
- **Datos de prueba:** validar con `seed_test_data` que haya volumen suficiente
  (`train_model` exige ≥10 muestras).

> **Estado:** Fases 0, 1, 2, 3, 4 y 5 completadas (2026-06-23). Plan de implementación finalizado.
