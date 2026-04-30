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

## Responsabilidades de Capas

1.  **Models**: Almacenan los resultados procesados del motor de riesgo.
2.  **Repositories**: Centralizan las consultas de estudiantes con mayor prioridad (High Risk).
3.  **Services**: Orquestan la recuperación del perfil completo de riesgo combinando scores y snapshots.
