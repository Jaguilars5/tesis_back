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

### StudentRiskScore (Puntaje de Riesgo)
Puntuación de riesgo calculada para un estudiante.

| Campo | Tipo | Verbose Name |
| :--- | :--- | :--- |
| `student` | ForeignKey (Student) | Estudiante |
| `academic_period` | ForeignKey (Academic_Period) | Período Académico |
| `risk_score` | DecimalField | Puntaje de Riesgo |
| `risk_label` | CharField (20) | Etiqueta de Riesgo |
| `top_factors` | JSONField | Factores Principales |
| `model_version` | CharField (50) | Versión del Modelo |
| `calculated_at` | DateTimeField | Fecha de Cálculo |

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
