# Modelo de Riesgo Académico

## Índice

1. [Arquitectura general](#1-arquitectura-general)
2. [Variables de entrada (features)](#2-variables-de-entrada-features)
3. [Variable objetivo (target)](#3-variable-objetivo-target)
4. [Motores de cálculo](#4-motores-de-c%C3%A1lculo)
   - 4.1 [Motor de reglas (fallback)](#41-motor-de-reglas-fallback)
   - 4.2 [Motor ML (regresión logística)](#42-motor-ml-regresi%C3%B3n-log%C3%ADstica)
5. [Flujo de entrenamiento del modelo ML](#5-flujo-de-entrenamiento-del-modelo-ml)
6. [Variables de salida](#6-variables-de-salida)
7. [Correlaciones esperadas](#7-correlaciones-esperadas)
8. [Presets y configuración](#8-presets-y-configuraci%C3%B3n)
9. [Modelos de datos (DB)](#9-modelos-de-datos-db)
10. [Cómo ejecutar](#10-c%C3%B3mo-ejecutar)

---

## 1. Arquitectura general

El sistema de riesgo académico tiene dos componentes que trabajan en cadena:

```
Seed de datos (seed_test_data.py)
  ↓
  Crea: StudentFeatureSnapshot (features)
  Crea: PeriodGradeSummary.is_failing (target real)
  Crea: StudentRiskScore (score usando motor de reglas)
  ↓
Entrenamiento (python manage.py train_risk_model)
  ↓
  Lee: StudentFeatureSnapshot + PeriodGradeSummary
  Entrena: LogisticRegression sobre 15 features
  Guarda: risk_model.joblib (artifact)
  ↓
Inferencia (risk_engine.calculate_risk)
  ↓
  Si engine == "ML" y existe artifact → LogisticRegression.predict_proba()
  Si no → motor de reglas (fallback)
  → StudentRiskScore (score + nivel)
```

### Flujo por período académico

```
Por cada estudiante en cada trimestre:
  1. AcademicRiskFeatureBuilder.build()
     → snapshot con {conducta, asistencia, calificaciones}
  2. AcademicRiskFeatureBuilder.build_persistence_metrics()
     → métricas planas + datos demográficos
  3. Se persiste StudentFeatureSnapshot
  4. calculate_risk(snapshot, metrics)
     → {semaforo_riesgo: {nivel, puntaje}, detalle_por_variable}
  5. Se persiste StudentRiskScore
```

---

## 2. Variables de entrada (features)

### 2.1 Feature engineering

Cada snapshot se construye desde 3 fuentes:

**Conducta** (`ConductIncidentRepository`):
| Variable snapshot | Descripción | Rango |
|------------------|-------------|-------|
| `faltas_leves` | Incidentes severidad LEVE | 0+ |
| `faltas_moderadas` | Incidentes severidad MODERADA | 0+ |
| `faltas_graves` | Incidentes severidad GRAVE/MUY_GRAVE | 0+ |
| `ratio_notificacion_familiar` | Fracción donde se notificó al representante | 0.0–1.0 |

**Asistencia** (`AttendanceRepository`):
| Variable snapshot | Descripción | Rango |
|------------------|-------------|-------|
| `porcentaje_asistencia` | % de registros con estado "P" (Presente) | 0–100 |
| `total_faltas` | Justificadas + injustificadas | 0+ |
| `faltas_justificadas` | Con estado "J" | 0+ |
| `faltas_injustificadas` | Con estado "A" (Ausente) | 0+ |
| `tardanzas` | Con estado "T" | 0+ |
| `total_registros` | Total de registros de asistencia en el período | 0+ |
| `max_faltas_consecutivas` | Racha máxima de A/J consecutivos | 0+ |

**Calificaciones** (`StudentNoteRepository`):
| Variable snapshot | Descripción | Rango |
|------------------|-------------|-------|
| `promedio_actual` | Media de notas normalizadas | 0–10 |
| `ultimo_examen` | Nota del último EXAMEN (o última nota) | 0–10 |
| `tendencia_notas` | Pendiente: (última - primera) / (n-1) | -10 a +10 |
| `total_calificaciones` | Número de actividades evaluadas | 0+ |
| `materias_reprobadas` | Conteo desde `PeriodGradeSummary.is_failing` | 0+ |

### 2.2 Features canónicas (16 columnas del modelo)

Orden canónico exacto (`FEATURE_COLUMNS` en `apps/analytics/ml/features.py`):

```python
FEATURE_COLUMNS = [
    "attendance_rate",           # Asistencia
    "consecutive_absences_max",
    "tardiness_count",
    "justified_absences",
    "unjustified_absences",
    "formative_avg_normalized",  # Calificaciones
    "summative_avg_normalized",
    "grade_trend_slope",
    "failing_subjects_count",    # Se excluye del entrenamiento (data leakage)
    "conduct_score",             # Conducta
    "severe_incidents_count",
    "family_notified_ratio",
    "prev_period_avg_grade",     # Históricas / Demográficas
    "age_grade_gap",
    "is_repeat",
    "has_special_needs",
]
```

**Features de entrenamiento** (`TRAIN_FEATURES`, 15 columnas):
Se excluye `failing_subjects_count` porque tiene correlación directa con el target (si `count > 0` entonces `is_failing = True` siempre). Incluirla sería **data leakage** y el modelo aprendería una regla trivial en lugar de patrones predictivos reales.

### 2.3 Cálculo de `conduct_score`

```python
conduct_score = max(0, 10 - (leves * 0.50 + moderadas * 1.00 + graves * 2.00))
```

Rango: 0–10. Penaliza conducta negativa: cada falta leve resta 0.5, cada moderada resta 1.0, cada grave resta 2.0.

### 2.4 Cálculo de `age_grade_gap`

```python
edad_real = (period.start_date - person.birth_date).days // 365
edad_esperada = 5 + school_year.grade_level  # 5 años al entrar a 1ro + años cursados
age_grade_gap = max(0, edad_real - edad_esperada)
```

Mide el desfase edad-grado. Un estudiante de 3ro con 18+ años tiene gap > 0.

### 2.5 Cálculo de `grade_trend_slope` (tendencia)

```python
if len(notas) < 2:
    tendencia = 0.0
else:
    tendencia = (última_nota - primera_nota) / (len(notas) - 1)
```

Positivo = mejora progresiva. Negativo = empeoramiento.

---

## 3. Variable objetivo (target)

Es un **target ordinal multi-clase** (0, 1, 2) que representa el **conteo de materias reprobadas**:

```python
count = PeriodGradeSummary.objects.filter(
    enrollment_id=X,
    academic_period_id=Y,
    is_failing=True
).count()
target = 2 if count >= 2 else count
```

- **Target = 0**: El estudiante aprobó todas las materias (ninguna con `final_avg < 7.00`).
- **Target = 1**: El estudiante reprobó exactamente 1 materia.
- **Target = 2**: El estudiante reprobó 2+ materias.

### Distribución esperada (seed)

| Target | % esperado | Descripción |
|--------|-----------|-------------|
| 0 (ninguna) | ~70% | Perfil normal: promedio 7.0-9.4, materia débil no baja de 7.0 |
| 1 (exactamente 1) | ~15% | Perfil normal con materia débil < 7.0, o riesgo medio con solo 1 |
| 2 (2+ materias) | ~15% | Perfil failing (todas < 7.0) o riesgo medio con 2+ materias débiles |

---

## 4. Motores de cálculo

El sistema tiene **2 motores** seleccionables mediante `RiskScoringConfig.engine` (campo en BD).

### 4.1 Motor de reglas (fallback)

Usa pesos fijos y umbrales configurables. Es el **motor por defecto** cuando no existe modelo ML entrenado.

#### Paso 1: Riesgo por dimensión (0–100)

```python
riesgo_conducta     = min(100, leves*5 + moderadas*10 + graves*25)
riesgo_asistencia   = 100 - porcentaje_asistencia
riesgo_calificaciones = min(100, ((10 - promedio) / 10 * 100) + materias_reprobadas * 15)
```

#### Paso 2: Puntaje bruto ponderado

```python
raw_score = riesgo_conducta * 0.30
          + riesgo_asistencia * 0.35
          + riesgo_calificaciones * 0.35
```

#### Paso 3: Nivel por umbrales de variables

| Condición | Nivel |
|-----------|-------|
| `asistencia < 70` O `promedio < 6.0` O `graves > 3` | **Rojo** |
| `asistencia 70–85` O `promedio 6.0–7.0` O `leves > 5` | **Amarillo** |
| Ninguna de las anteriores | **Verde** |

#### Paso 4: Ajuste del score según nivel

```python
if nivel == "rojo":     score = max(raw_score, 70)
if nivel == "amarillo": score = max(raw_score, 40)
if nivel == "verde":    score = min(raw_score, 39.99)
```

#### Paso 5: Clasificación final

```python
if score >= 70:  → "rojo"
if score >= 40:  → "amarillo"
else:            → "verde"
```

### 4.2 Motor ML (regresión logística)

#### Algoritmo

```python
LogisticRegression(
    class_weight="balanced",  # Compensa desbalance entre clases
    C=1.0,                    # Regularización inversa (C grande = menos regularización)
    solver="lbfgs",           # Optimizador para datasets medianos
    max_iter=2000,
    random_state=42,
    multi_class="multinomial",  # Modelo ordinal: P(0), P(1), P(2+)
)
```

#### Preprocesamiento

```python
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Media 0, desviación estándar 1
```

#### Inferencia

```python
proba = model.predict_proba(X_scaled)[0]     # [P(0), P(1), P(2+)]
score = proba[2] * 100                       # P(2+) * 100 → 0–100 (para semáforo)
```

- `P(0)`: probabilidad de 0 materias reprobadas
- `P(1)`: probabilidad de exactamente 1 materia reprobada
- `P(2+)`: probabilidad de 2+ materias reprobadas → se usa como `puntaje_riesgo`

#### Validación cruzada

```python
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_scaled, y, cv=cv, scoring="accuracy")
```

Se reporta Accuracy promedio ± desviación estándar.

#### Interpretación del score

El score ML es **P(2+ materias reprobadas) × 100**, es decir, la probabilidad porcentual de fracaso general. Los mismos umbrales del motor de reglas se aplican:

| Score | Nivel |
|-------|-------|
| ≥ 70  | 🔴 Rojo |
| 40–69 | 🟡 Amarillo |
| < 40  | 🟢 Verde |

Adicionalmente se incluye la distribución completa: `P(0)`, `P(1)` y las materias específicas reprobadas.

#### Coeficiente de las features

Para cada clase k (0, 1, 2), `model.coef_[k]` contiene los pesos aprendidos. El signo indica la dirección de la correlación:

| Coeficiente positivo | Coeficiente negativo |
|---------------------|---------------------|
| A mayor valor, mayor riesgo | A mayor valor, menor riesgo |
| Ej: `consecutive_absences_max` | Ej: `attendance_rate` |
| Ej: `age_grade_gap` | Ej: `formative_avg_normalized` |

La magnitud absoluta del coeficiente indica la **importancia relativa** de la feature en la decisión del modelo (asumiendo features escaladas).

---

## 5. Flujo de entrenamiento del modelo ML

### 5.1 Origen de los datos

Los datos provienen del comando `seed_test_data.py` que genera 3 años históricos:

| Año | Estudiantes | Snapshots generados |
|-----|-------------|-------------------|
| 2023-2024 | 180 (60×3 grados) | 540 (180×3 trimestres) |
| 2024-2025 | 180 | 540 |
| 2025-2026 | 180 | 540 |
| **Total** | **~282 únicos** | **1,620** |

### 5.2 Proceso de entrenamiento

```
python manage.py train_risk_model
```

```
1. Carga todos los StudentFeatureSnapshot (1,620 registros)
2. Para cada snapshot, obtiene el target real:
   - Consulta PeriodGradeSummary.enrollment_id, academic_period_id
   - Si is_failing=True → target=1, sino target=0
3. Construye matriz X (1,620 × 15 features)
4. Construye vector y (1,620 × 1, valores 0/1)
5. Escala features con StandardScaler (media=0, std=1)
6. Entrena LogisticRegression con class_weight="balanced"
7. Validación cruzada StratifiedKFold(5) → ROC-AUC
8. Reporte de clasificación y coeficientes
9. Guarda artifact: risk_model.joblib
   Contenido: {model, scaler, features, mean, std}
```

### 5.3 Distribución esperada del target

Con ~15% de estudiantes reprobados por año:
- **Target = 1**: ~243 registros (15%)
- **Target = 0**: ~1,377 registros (85%)

`class_weight="balanced"` asigna pesos inversamente proporcionales a la frecuencia de cada clase:

```python
peso_clase_0 = total / (2 * count_0)  # ~0.59 para 1,377/1,620
peso_clase_1 = total / (2 * count_1)  # ~3.33 para 243/1,620
```

Esto evita que el modelo aprenda a predecir siempre "aprobado" (clase mayoritaria).

### 5.4 Qué features son más importantes

Dado el diseño del seed, el orden de importancia esperado es:

| Rank | Feature | Coef. esperado | Explicación |
|------|---------|---------------|-------------|
| 1 | `formative_avg_normalized` | Fuerte negativo (~ -2.0) | Promedio < 7.0 casi siempre → is_failing |
| 2 | `summative_avg_normalized` | Fuerte negativo (~ -1.8) | Same que formativo |
| 3 | `attendance_rate` | Moderado negativo (~ -0.5) | Reprobados tienen 58-80%, aprobados 84-97% |
| 4 | `grade_trend_slope` | Débil negativo (~ -0.3) | Tendencia negativa correlaciona con fracaso |
| 5 | `consecutive_absences_max` | Débil positivo (~ +0.3) | Rachas largas en reprobados |
| 6 | `severe_incidents_count` | Débil positivo (~ +0.2) | Solo algunos reprobados tienen incidentes |
| 7 | `is_repeat` | Débil positivo (~ +0.2) | Repitentes tienen más riesgo |
| 8 | `age_grade_gap` | Débil positivo (~ +0.15) | Mayor brecha → mayor riesgo |
| 9 | `has_special_needs` | Débil positivo (~ +0.1) | Pocos casos (~6) |
| 10 | `prev_period_avg_grade` | Débil negativo (~ -0.3) | Historial de notas previas |
| 11 | `tardiness_count` | Muy débil positivo (~ +0.1) | Poca varianza |
| 12 | `conduct_score` | Muy débil negativo (~ -0.1) | Poca varianza |
| 13 | `family_notified_ratio` | Débil positivo (~ +0.1) | Depende de incidentes |

**Nota**: Estas correlaciones son las impuestas por el seed. Con datos reales de un colegio, las correlaciones serán distintas y el modelo ML las descubrirá automáticamente.

---

## 6. Variables de salida

### 6.1 StudentRiskScore (persistido en DB)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `enrollment` | FK → students.Enrollment | Matrícula del estudiante |
| `academic_period` | FK → academic_period.AcademicPeriod | Período evaluado |
| `risk_score` | Decimal(5,2) | Puntaje 0.00–100.00 |
| `risk_label` | CharField(20) | "rojo", "amarillo" o "verde" |
| `model_version` | CharField(50) | Trazabilidad (reglas + preset o sklearn) |
| `calculated_at` | DateTime | Timestamp |

Unicidad garantizada por: `(enrollment, academic_period, model_version)`.

### 6.2 Salida de `calculate_risk()` (JSON)

```json
{
  "estudiante_id": "123",
  "periodo": "456",
  "fecha_analisis": "2026-01-15T10:30:00+00:00",
  "semaforo_riesgo": {
    "nivel": "rojo",
    "puntaje_riesgo": 78.5,
    "factores_criticos": [
      "3 materias reprobadas - riesgo academico",
      "Promedio academico en nivel critico (rojo)"
    ],
    "recomendaciones": [
      "Planificar refuerzo academico integral en materias con bajo rendimiento",
      "Revisar plan de asistencia y contactar al representante"
    ]
  },
  "detalle_por_variable": {
    "conducta":       { "nivel": "verde",   "peso": 0.30 },
    "asistencia":     { "nivel": "amarillo", "peso": 0.35 },
    "calificaciones": { "nivel": "rojo",     "peso": 0.35 }
  },
  "model_version": "sklearn-joblib-v2",
  "distribucion_materias": {
    "prob_0_reprobadas": 0.05,
    "prob_1_reprobada": 0.12,
    "prob_2_o_mas": 0.83
  },
  "materias_reprobadas": [
    { "nombre": "Matematica", "nota_final": 4.5 },
    { "nombre": "Fisica", "nota_final": 5.2 },
    { "nombre": "Quimica", "nota_final": 6.8 }
  ]
}
```

**Campos adicionales (cuando motor=ML):**

| Campo | Descripción |
|-------|-------------|
| `distribucion_materias.prob_0_reprobadas` | P(0) — probabilidad de ninguna reprobada |
| `distribucion_materias.prob_1_reprobada` | P(1) — probabilidad de exactamente 1 |
| `distribucion_materias.prob_2_o_mas` | P(2+) — probabilidad de 2+ (es el `puntaje_riesgo / 100`) |
| `distribucion_materias.prediccion_clase` | Clase más probable: 0, 1 o 2 |
| `materias_reprobadas[]` | Lista de materias con `is_failing=True` y su nota final |

### 6.3 Semáforo de riesgo

| Nivel | Score | Color | Acción |
|-------|-------|-------|--------|
| Rojo | ≥ 70 | 🔴 | Intervención crítica inmediata |
| Amarillo | ≥ 40 y < 70 | 🟡 | Monitoreo y apoyo preventivo |
| Verde | < 40 | 🟢 | Seguimiento regular |

---

## 7. Correlaciones esperadas

### 7.1 Matriz de correlación (basada en seed)

```
                          is_failing  avg_grade  attend.rate  conduct  is_repeat
is_failing                  1.00      -0.75       -0.45        -0.10    0.20
avg_grade_normalized       -0.75       1.00        0.40         0.08   -0.15
attendance_rate            -0.45       0.40        1.00         0.05   -0.10
grade_trend_slope          -0.25       0.35        0.10         0.02   -0.05
consecutive_absences_max    0.30      -0.25       -0.55        -0.03    0.08
tardiness_count             0.15      -0.10       -0.20         0.02    0.03
conduct_score              -0.10       0.08        0.05         1.00   -0.02
severe_incidents_count      0.15      -0.10       -0.05        -0.40    0.05
is_repeat                   0.20      -0.15       -0.10        -0.02    1.00
age_grade_gap               0.10      -0.10       -0.05        -0.01    0.15
has_special_needs           0.08      -0.05       -0.03        -0.01    0.02
prev_period_avg_grade      -0.60       0.55        0.30         0.05   -0.10
```

### 7.2 Interpretación

**Correlaciones fuertes** (|r| > 0.5):
- `avg_grade_normalized` vs `is_failing` (-0.75): El predictor más fuerte. Los reprobados tienen notas bajas.
- `prev_period_avg_grade` vs `is_failing` (-0.60): El historial importa.

**Correlaciones moderadas** (|r| 0.3–0.5):
- `attendance_rate` vs `is_failing` (-0.45): Baja asistencia → mayor riesgo.
- `consecutive_absences_max` vs `attendance_rate` (-0.55): Rachas de ausencia asociadas a baja asistencia.

**Correlaciones débiles** (|r| < 0.3):
- Conducta con riesgo: Baja correlación porque pocos estudiantes tienen incidentes.
- Demográficas: `is_repeat` (0.20) y `age_grade_gap` (0.10) aportan información marginal.

### 7.3 Efecto del seed en las correlaciones

Las correlaciones reflejan directamente las reglas del seed:

| Perfil | Promedio | Asistencia | Conducta | Tasa esperada |
|--------|----------|-----------|----------|---------------|
| Reprobado (~15%) | 4.0–6.4 | 58–80% | 20% tienen incidentes | 100% is_failing |
| Riesgo medio (~15%) | 5.4–7.6 | 70–88% | Variable | ~50% is_failing |
| Normal (~70%) | 7.0–9.4 | 84–97% | 14% tienen outliers | ~0% is_failing |

Esto crea una separación artificial clara. En un colegio real, las fronteras son más difusas.

---

## 8. Presets y configuración

### 8.1 Presets disponibles

| Preset | Conducta | Asistencia | Calificaciones | Sensibilidad |
|--------|----------|-----------|---------------|--------------|
| **Equilibrado** (default) | 30% | 35% | 35% | Media |
| **Conservador** | 25% | 40% | 35% | Alta (detecta riesgo antes) |
| **Estricto** | 35% | 30% | 35% | Baja (solo extremos) |

### 8.2 Umbrales por preset

| Umbral | Equilibrado | Conservador | Estricto |
|--------|-------------|-------------|----------|
| score_red_min (rojo ≥) | 70 | 68 | 72 |
| score_yellow_min (amarillo ≥) | 40 | 38 | 42 |
| attendance_red_max (rojo <) | 70% | 75% | 60% |
| attendance_yellow_max | 85% | 90% | 80% |
| average_red_max (rojo <) | 6.0 | 6.5 | 5.0 |
| average_yellow_max | 7.0 | 7.5 | 6.5 |
| severe_red_min (graves >) | 3 | 2 | 4 |
| mild_yellow_min (leves >) | 5 | 4 | 6 |

### 8.3 Configurable en BD

La tabla `analytics_riskscoringconfig` (singleton, pk=1) externaliza todos los valores. Si no existe fila en BD, se usan los defaults seguros del preset **Equilibrado**.

---

## 9. Modelos de datos (DB)

### 9.1 StudentFeatureSnapshot

Almacena el vector de features completo para reproducibilidad.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `enrollment` | FK | Matrícula |
| `academic_period` | FK | Período |
| `attendance_rate` | Decimal(5,2) | % asistencia |
| `consecutive_absences_max` | Integer | Rachas |
| `tardiness_count` | Integer | Atrasos |
| `justified_absences` | Integer | Faltas justificadas |
| `unjustified_absences` | Integer | Faltas injustificadas |
| `formative_avg_normalized` | Decimal(5,2) | Promedio formativo |
| `summative_avg_normalized` | Decimal(5,2) | Promedio sumativo |
| `grade_trend_slope` | Decimal(5,2) | Tendencia |
| `failing_subjects_count` | Integer | Materias reprobadas |
| `conduct_score` | Decimal(5,2) | Score conducta (0–10) |
| `severe_incidents_count` | Integer | Incidentes graves |
| `family_notified_ratio` | Decimal(5,2) | Ratio notificación |
| `prev_period_avg_grade` | Decimal(5,2) nullable | Promedio período anterior |
| `age_grade_gap` | Integer | Brecha edad-grado |
| `is_repeat` | Boolean | Repitente |
| `has_special_needs` | Boolean | NEE |
| `city` | FK nullable | Ciudad de origen |
| `special_needs_type` | FK nullable | Tipo NEE |
| `withdrawal_reason` | FK nullable | Motivo retiro |

Unicidad: `(enrollment, academic_period)`.

### 9.2 StudentRiskScore

Almacena el resultado del cálculo.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `enrollment` | FK | Matrícula |
| `academic_period` | FK | Período |
| `risk_score` | Decimal(5,2) | Puntaje 0–100 |
| `risk_label` | CharField(20) | rojo/amarillo/verde |
| `model_version` | CharField(50) | Versión del modelo |
| `calculated_at` | DateTime | Fecha de cálculo |

Unicidad: `(enrollment, academic_period, model_version)`.

### 9.3 RiskScoringConfig (singleton)

Configuración global del motor.

| Campo | Default | Descripción |
|-------|---------|-------------|
| `engine` | "reglas" | Motor activo (reglas/ML) |
| `preset` | "equilibrado" | Preset base |
| `weight_conducta` | 30% | Peso conducta |
| `weight_asistencia` | 35% | Peso asistencia |
| `weight_calificaciones` | 35% | Peso calificaciones |
| `score_red_min` | 70 | Mínimo para rojo |
| `score_yellow_min` | 40 | Mínimo para amarillo |
| (13 umbrales más) | ... | Ver sección 8.2 |

---

## 10. Cómo ejecutar

### 10.1 Generar datos de prueba

```bash
python manage.py seed_catalogs
python manage.py seed_permissions
python manage.py seed_test_data
```

Esto genera **1,620 snapshots** (180 estudiantes × 3 trimestres × 3 años).

### 10.2 Entrenar modelo ML

```bash
python manage.py train_risk_model
```

Carga todos los snapshots, entrena la regresión logística y guarda `apps/analytics/ml/risk_model.joblib`.

### 10.3 Activar motor ML

Opción A — Cambiar en BD:
```sql
UPDATE analytics_riskscoringconfig SET engine = 'ML' WHERE id = 1;
```

Opción B — Desde el panel de administración de Django:
- Ir a `RiskScoringConfig` (singleton, pk=1)
- Cambiar `engine` de "reglas" a "ML"

### 10.4 Verificar modelo

```bash
python manage.py test apps.analytics.tests.test_risk_model
```

### 10.5 Calcular riesgo para un estudiante

```python
from apps.analytics.tasks import calculate_academic_risk
from apps.analytics.services.feature_builder import AcademicRiskFeatureBuilder

builder = AcademicRiskFeatureBuilder(student_id=123, academic_period_id=456)
snapshot = builder.build()
metrics = builder.build_persistence_metrics(snapshot)
analysis = calculate_academic_risk(snapshot, metrics)
# → {"semaforo_riesgo": {"nivel": "rojo", "puntaje_riesgo": 78.5, ...}}
```
