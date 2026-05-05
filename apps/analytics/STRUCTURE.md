# Estructura Técnica: Módulo `analytics`

Este documento detalla la organización interna del módulo de análisis de datos.

## Árbol de Directorios

```text
analytics/
├── api/                  # Capa de Entrada (REST)
│   ├── serializers.py    # Esquemas para Scores y Snapshots
│   ├── views.py          # Vistas basadas en funciones (POST)
│   └── urls.py           # Definición de rutas específicas
├── models/               # Capa de Datos (Entidades)
│   ├── student_risk_score.py
│   └── student_feature_snapshot.py
├── repositories/         # Capa de Persistencia (Queries)
│   ├── __init__.py
│   └── (clases internas) # Queries de ordenamiento por riesgo
├── services/             # Capa de Negocio (Orquestación)
│   └── analytics_service.py # Lógica de perfiles de riesgo
└── tests/                # Suites de Pruebas
    └── (test suites)     # Validación de reportes de riesgo
```

## Flujo de Trabajo Recomendado

`API View` → `Service` → `Repository` → `Model`

## Guía de Importación

### ✅ Prácticas Correctas
```python
from apps.analytics.services.analytics_service import AnalyticsService
from apps.analytics.models import StudentRiskScore
```

## Riesgo Academico v1

El modulo incluye un flujo asincrono para calcular riesgo academico con
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
- `ml/risk_model.joblib`: ubicacion esperada del modelo entrenado.
- `ml/.gitkeep`: conserva el directorio de modelos.

Contrato de salida de la task:

```json
{
  "estudiante_id": "string",
  "periodo": "string",
  "fecha_analisis": "datetime",
  "semaforo_riesgo": {
    "nivel": "rojo|amarillo|verde",
    "puntaje_riesgo": 0.0,
    "factores_criticos": [],
    "recomendaciones": []
  },
  "detalle_por_variable": {
    "conducta": { "nivel": "string", "peso": 0.3 },
    "asistencia": { "nivel": "string", "peso": 0.35 },
    "calificaciones": { "nivel": "string", "peso": 0.35 }
  }
}
```

`model_version` se usa internamente para persistir `StudentRiskScore`, pero no
se expone en la respuesta publica de la task.

## Responsabilidades de Capas

1.  **Models**: Almacenan los resultados procesados del motor de riesgo.
2.  **Repositories**: Centralizan las consultas de estudiantes con mayor prioridad (High Risk).
3.  **Services**: Orquestan la recuperación del perfil completo de riesgo combinando scores y snapshots.
