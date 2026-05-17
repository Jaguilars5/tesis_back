# Módulo `analytics` — Procesamiento de Datos y Riesgo

Este módulo se encarga del análisis de datos académicos y disciplinarios para generar perfiles de riesgo y snapshots de métricas, permitiendo la identificación temprana de estudiantes que requieren intervención.

Su diseño utiliza un motor de procesamiento que captura el estado del estudiante en momentos específicos para facilitar el seguimiento histórico.

---

## Estructura del Módulo

```
analytics/
├── models/         # Scores de riesgo y snapshots de variables
├── repositories/   # Consultas de alta prioridad y tendencias
├── services/       # Lógica de cálculo de perfiles de riesgo
├── api/            # Endpoints para consulta de métricas
└── tests/          # Validación de algoritmos de score
```

---

## Modelos de Datos

### RiskFactor (Factor de Riesgo)
Catálogo de factores de riesgo.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `code` | CharField (30) | Código único |
| `name` | CharField (100) | Nombre |
| `description` | TextField | Descripción |

### StudentFeatureSnapshot (Instantánea de Métricas)
Métricas de un estudiante para un período específico.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `student` | ForeignKey (Student) | Estudiante |
| `academic_period` | ForeignKey (Academic_Period) | Período académico |
| `attendance_rate` | DecimalField | Tasa de asistencia (0-1) |
| `consecutive_absences_max` | IntegerField | Máximo de faltas consecutivas |
| `tardiness_count` | IntegerField | Cantidad de atrasos |
| `avg_grade_normalized` | DecimalField | Promedio normalizado (base 10) |
| `grade_trend_slope` | DecimalField | Tendencia de notas |
| `failing_subjects_count` | IntegerField | Materias reprobadas |
| `conduct_score` | DecimalField | Puntaje de conducta |
| `family_notified_ratio` | DecimalField | Ratio de notificación familiar |
| `prev_period_avg_grade` | DecimalField | Promedio período anterior |
| `age_grade_gap` | IntegerField | Brecha edad-grado |
| `calculated_at` | DateTimeField | Fecha de cálculo |

### StudentRiskScore (Puntaje de Riesgo)
Puntuación de riesgo calculada para un estudiante.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `student` | ForeignKey (Student) | Estudiante |
| `academic_period` | ForeignKey (Academic_Period) | Período académico |
| `risk_score` | DecimalField | Puntaje de riesgo |
| `risk_label` | CharField (20) | Etiqueta de riesgo |
| `model_version` | CharField (50) | Versión del modelo |
| `calculated_at` | DateTimeField | Fecha de cálculo |

### StudentRiskFactor (Factor de Riesgo del Estudiante)
Asociación entre puntaje de riesgo y factor.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `student_risk_score` | ForeignKey (StudentRiskScore) | Puntaje de riesgo |
| `risk_factor` | ForeignKey (RiskFactor) | Factor de riesgo |
| `contribution_weight` | DecimalField | Peso de contribución (%) |

---

## Capa de Servicios

### AnalyticsService (Orquestador)

- `get_student_risk_profile`: Genera un reporte consolidado que incluye el puntaje de riesgo más reciente del estudiante y la instantánea (snapshot) de métricas académicas utilizadas para dicho cálculo.
- `list_priority_students`: Proporciona una lista de estudiantes ordenados por nivel de criticidad (riesgo alto), permitiendo a las instituciones priorizar sus intervenciones pedagógicas.

---

## Endpoints

### StudentRiskScore

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/analytics/student-risk-scores/` | Listar puntajes de riesgo | analytics.view_risk_score |
| GET | `/api/analytics/student-risk-scores/{id}/` | Detalle | analytics.view_risk_score |

### StudentFeatureSnapshot

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/analytics/feature-snapshots/` | Listar snapshots | analytics.view_feature_snapshot |
| GET | `/api/analytics/feature-snapshots/{id}/` | Detalle | analytics.view_feature_snapshot |

### StudentRiskFactor

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/analytics/student-risk-factors/` | Listar factores | analytics.view_risk_factor |
| GET | `/api/analytics/student-risk-factors/{id}/` | Detalle | analytics.view_risk_factor |

### RiskFactor

| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/analytics/risk-factors/` | Listar factores | analytics.view_risk_factor |
| POST | `/api/analytics/risk-factors/` | Crear factor | analytics.create_risk_factor |

---

## Seguridad

### Autenticación y Permisos

Todos los endpoints requieren:
1. Header `Authorization: Bearer <token>`
2. Permiso específico del usuario

### Permisos por modelo

| Modelo | Ver |
|--------|-----|
| StudentRiskScore | analytics.view_risk_score |
| StudentFeatureSnapshot | analytics.view_feature_snapshot |

Seedear permisos:
```bash
python manage.py seed_permissions --module analytics
```

---

## Pruebas

```
DJANGO_SETTINGS_MODULE=config.settings.test python manage.py test apps.analytics
```

---

## Modelo de Riesgo Academico

El flujo v1 de riesgo academico se implementa dentro de `apps.analytics` y
combina snapshots desde `grading`, reglas de negocio y un modelo ML opcional.

### Construccion del snapshot

`apps.analytics.services.feature_builder.AcademicRiskFeatureBuilder` construye
el JSON de entrada del modelo usando datos de:

- `StudentNote`: promedio actual, materias reprobadas y ultimo examen.
- `Attendance`: porcentaje de asistencia, faltas justificadas, faltas
  injustificadas, tardanzas y maximo de faltas consecutivas.
- `ConductIncident`: faltas leves, moderadas, graves, observaciones recientes
  y ratio de notificacion familiar.

El builder tambien genera las metricas persistibles para
`StudentFeatureSnapshot` y valida rangos basicos: asistencia `0-100`, notas
`0-10` y contadores no negativos.

### Calculo asincrono

La task principal es:

```python
calculate_student_academic_risk_task.delay(student_id, academic_period_id)
```

Flujo:

1. Construye snapshot.
2. Persiste `StudentFeatureSnapshot`.
3. Intenta cargar `apps/analytics/ml/risk_model.joblib`.
4. Si el modelo no existe o falla, usa fallback de reglas + puntaje ponderado.
5. Persiste `StudentRiskScore`.
6. Retorna el JSON estandarizado de salida.

### Reglas v1 del semaforo

- `rojo`: asistencia menor a 70%, promedio menor a 6.0 o mas de 3 faltas graves.
- `amarillo`: asistencia entre 70% y 85%, promedio entre 6.0 y 7.0 o mas de 5 faltas leves.
- `verde`: asistencia mayor a 85%, promedio mayor a 7.0 y sin faltas graves.

### Puntaje fallback

Si no existe un modelo `.joblib`, el sistema calcula un puntaje `0-100` con:

- Conducta: 30%.
- Asistencia: 35%.
- Calificaciones: 35%.

El resultado mantiene explicabilidad mediante `factores_criticos`,
`recomendaciones` y `detalle_por_variable`.
