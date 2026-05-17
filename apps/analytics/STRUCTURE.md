# Estructura Técnica: Módulo `analytics`

Este documento detalla la organización interna del módulo de análisis de datos.

## Árbol de Directorios

```text
analytics/
├── api/                  # Capa de Entrada (REST)
│   ├── serializers.py    # Esquemas para Scores y Snapshots
│   ├── views.py          # ViewSets REST
│   └── urls.py           # Definición de rutas
├── models/               # Capa de Datos (Entidades)
│   ├── risk_factor.py           # Catálogo de factores de riesgo
│   ├── student_feature_snapshot.py # Métricas de un estudiante
│   ├── student_risk_score.py    # Puntaje de riesgo
│   └── student_risk_factor.py   # Asociación score-factor
├── repositories/         # Capa de Persistencia (Queries)
│   └── (clases internas) # Queries de ordenamiento por riesgo
├── services/             # Capa de Negocio (Orquestación)
│   └── analytics_service.py # Lógica de perfiles de riesgo
├── tasks.py              # Tasks Celery para cálculo async
├── ml/                   # Modelos ML entrenados
│   └── risk_model.joblib # Modelo de predicción de riesgo
└── tests/                # Suites de Pruebas
```

## Modelos de Datos

### RiskFactor
Catálogo de factores de riesgo (ej: "Baja Asistencia", "Bajo Rendimiento").

### StudentFeatureSnapshot
Instantánea de métricas de un estudiante para un período específico. Estas métricas sirven como entrada para el modelo de predicción.

### StudentRiskScore
Puntaje de riesgo calculado para un estudiante en un período.

### StudentRiskFactor
Asociación entre un puntaje de riesgo y los factores que contribuyen a ese score.

## Flujo de Trabajo Recomendado

`API View` → `Service` → `Repository` → `Model`

## Guía de Importación

### ✅ Prácticas Correctas
```python
from apps.analytics.services.analytics_service import AnalyticsService
from apps.analytics.models import StudentRiskScore, StudentFeatureSnapshot, RiskFactor
```

## Riesgo Académico v1

El módulo incluye un flujo asíncrono para calcular riesgo académico con
snapshots de `grading`, un artefacto ML opcional y fallback de reglas.

Flujo:

```text
Celery task
  -> AcademicRiskFeatureBuilder
  -> Grading repositories
  -> StudentFeatureSnapshot
  -> ML joblib opcional o fallback de reglas
  -> StudentRiskScore
  -> JSON estandarizado
```

Componentes:

- `services/feature_builder.py`: construye el snapshot desde asistencia,
  conducta y calificaciones.
- `tasks.py`: expone `calculate_student_academic_risk_task`.
- `ml/risk_model.joblib`: ubicación esperada del modelo entrenado.
- `ml/.gitkeep`: conserva el directorio de modelos.

### Semáforo de Riesgo v1

| Nivel | Condiciones |
|-------|-------------|
| Rojo | Asistencia < 70% O promedio < 6.0 O > 3 faltas graves |
| Amarillo | Asistencia 70-85% O promedio 6.0-7.0 O > 5 faltas leves |
| Verde | Asistencia > 85% Y promedio > 7.0 Y sin faltas graves |

### Puntaje Fallback

Si no existe `risk_model.joblib`, el sistema calcula un puntaje 0-100 con:
- Conducta: 30%
- Asistencia: 35%
- Calificaciones: 35%

El resultado mantiene explicabilidad mediante `risk_factors`.

## Responsabilidades de Capas

1.  **Models**: Almacenan los resultados procesados del motor de riesgo.
2.  **Repositories**: Centralizan las consultas de estudiantes con mayor prioridad (High Risk).
3.  **Services**: Orquestan la recuperación del perfil completo de riesgo combinando scores y snapshots.