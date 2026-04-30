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

## API REST (Resumen)

El módulo utiliza el patrón de acciones basadas en POST para consultas de datos.

### Riesgo Estudiantil
- POST `/api/analytics/student-risk/list/`
- POST `/api/analytics/student-risk/get/`

---

## Seguridad

Header requerido:

```
Authorization: Bearer <token>
```

---

## Pruebas

```
python manage.py test apps.analytics
```
