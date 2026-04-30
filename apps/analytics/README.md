# Módulo `analytics` — Predicción de Riesgo y Métricas Académicas

Este módulo se encarga de consolidar métricas de diversas áreas (asistencia, calificaciones, conducta) para generar indicadores de riesgo académico mediante modelos predictivos.

## Estructura de Carpetas

```
analytics/
├── models/                    # Capa de datos
│   ├── student_risk_score.py  # Resultado de predicción
│   └── student_feature_snapshot.py # Datos consolidados (entrada)
│
├── repositories/             # Capa de acceso a datos
│   └── analytics_repo.py
│
├── services/                 # Capa de lógica
│   └── analytics_service.py  # Gestión de perfiles de riesgo
│
├── api/                      # Capa HTTP
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── admin.py                  # Panel administrativo
├── apps.py                   # Configuración
└── README.md                 # Documentación
```

## Modelos Principales

### StudentFeatureSnapshot
Consolida métricas clave como tasa de asistencia, promedio normalizado, tendencia de notas y conducta en un momento dado. Es la "foto" del rendimiento del estudiante.

### StudentRiskScore
Almacena el nivel de riesgo calculado (Bajo, Medio, Alto) junto con los factores que más influyeron en dicha clasificación.

## Integración
Este módulo consume datos de `grading` (notas, asistencia) y `students` para generar sus reportes.

## API REST
- `/api/analytics/student-risk/list/` - Listar niveles de riesgo.
- `/api/analytics/feature-snapshot/get/` - Obtener métricas detalladas.
