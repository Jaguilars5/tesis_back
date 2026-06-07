# Módulo `analytics` — Procesamiento de Datos y Riesgo Académico

El módulo `analytics` se encarga del análisis de datos académicos, de asistencia y disciplinarios del sistema para generar instantáneas históricas de métricas y calcular perfiles de riesgo en tiempo real. Adicionalmente, cuenta con un sistema de alertas tempranas para facilitar las intervenciones tempranas por parte de docentes, psicólogos e inspectores.

---

## 🏛️ Arquitectura del Módulo

El módulo sigue la arquitectura en capas estándar del sistema:

```
analytics/
├── models/         # Definición de esquemas de BD (Riesgos, Snapshots y Alertas)
├── repositories/   # Encapsulamiento de queries complejas y ordenamiento ORM
├── services/       # Algoritmos de cálculo de riesgo y orquestación del motor ML/Reglas
├── api/            # Serializadores y ViewSets de Django REST Framework (DRF)
└── tests/          # Suite de pruebas unitarias e integración de cobertura de brechas
```

---

## 🗃️ Modelos de Datos Factibles

### 1. `RiskFactor` (Factor de Riesgo)

Catálogo maestro de factores de riesgo definidos a nivel del sistema.

| Campo         | Tipo Django      | Descripción                                     |
| :------------ | :--------------- | :---------------------------------------------- |
| `code`        | `CharField(30)`  | Código único identificador (ej: `ABSENTEEISM`). |
| `name`        | `CharField(100)` | Nombre descriptivo del factor.                  |
| `description` | `TextField`      | Explicación del comportamiento o causa.         |

### 2. `StudentFeatureSnapshot` (Instantánea de Métricas)

Captura el estado de las variables críticas de un estudiante para un periodo académico específico.

| Campo                      | Tipo Django     | Relación / Significado                                                 |
| :------------------------- | :-------------- | :--------------------------------------------------------------------- |
| `enrollment`               | `ForeignKey`    | `students.Enrollment` (Matrícula del estudiante).                      |
| `academic_period`          | `ForeignKey`    | `academic.Academic_Period` (Periodo correspondiente).                  |
| `attendance_rate`          | `DecimalField`  | Tasa de asistencia general (`0.00` a `100.00`).                        |
| `consecutive_absences_max` | `IntegerField`  | Pico máximo de faltas seguidas en el periodo.                          |
| `tardiness_count`          | `IntegerField`  | Contador acumulado de atrasos injustificados.                          |
| `justified_absences`       | `IntegerField`  | Total de inasistencias justificadas.                                   |
| `unjustified_absences`     | `IntegerField`  | Total de inasistencias injustificadas.                                 |
| `formative_avg_normalized` | `DecimalField`  | Promedio de notas formativas normalizado sobre 10.                     |
| `summative_avg_normalized` | `DecimalField`  | Promedio de notas sumativas normalizado sobre 10.                      |
| `grade_trend_slope`        | `DecimalField`  | Pendiente lineal de la tendencia académica actual.                     |
| `failing_subjects_count`   | `IntegerField`  | Cantidad de asignaturas con promedio menor al mínimo aprobatorio.      |
| `conduct_score`            | `DecimalField`  | Nota de conducta registrada en el periodo.                             |
| `severe_incidents_count`   | `IntegerField`  | Cantidad de incidentes conductuales calificados como graves.           |
| `family_notified_ratio`    | `DecimalField`  | Ratio de notificaciones enviadas y atendidas por los padres.           |
| `prev_period_avg_grade`    | `DecimalField`  | Promedio general del periodo anterior (para tendencias inter-periodo). |
| `age_grade_gap`            | `IntegerField`  | Brecha de edad del alumno en relación con su nivel escolar.            |
| `is_repeat`                | `BooleanField`  | Indica si el alumno está repitiendo el grado.                          |
| `has_special_needs`        | `BooleanField`  | Registra si cuenta con necesidades educativas especiales (NEE).        |
| `residential_zone`         | `CharField`     | Ubicación o sector geográfico de residencia.                           |
| `distance_to_school_km`    | `DecimalField`  | Distancia en kilómetros hasta el centro educativo.                     |
| `active_alerts`            | `IntegerField`  | Cantidad de alertas tempranas activas asociadas.                       |
| `calculated_at`            | `DateTimeField` | Timestamp de inserción automática del registro de snapshot.            |

### 3. `StudentRiskScore` (Puntaje de Riesgo del Estudiante)

Puntuación de riesgo acumulada ponderada calculada por el motor de inferencia analítica.

| Campo             | Tipo Django     | Relación / Significado                                       |
| :---------------- | :-------------- | :----------------------------------------------------------- |
| `enrollment`      | `ForeignKey`    | `students.Enrollment` (Matrícula del estudiante).            |
| `academic_period` | `ForeignKey`    | `academic.Academic_Period` (Periodo correspondiente).        |
| `risk_score`      | `DecimalField`  | Puntaje numérico calculado (`0.00` a `100.00`).              |
| `risk_label`      | `CharField(20)` | Nivel semafórico resultante: `"bajo"`, `"medio"` o `"alto"`. |
| `model_version`   | `CharField(50)` | Versión del modelo matemático/ML utilizado para el cálculo.  |
| `calculated_at`   | `DateTimeField` | Fecha y hora en que se calculó e ingresó el puntaje.         |

### 4. `StudentRiskFactor` (Factor de Riesgo Activo del Estudiante)

Detalle explicativo que asocia un puntaje de riesgo determinado con los factores gatillantes de dicho estado.

| Campo                 | Tipo Django    | Relación / Significado                                                    |
| :-------------------- | :------------- | :------------------------------------------------------------------------ |
| `student_risk_score`  | `ForeignKey`   | `StudentRiskScore` (Puntaje de riesgo asociado).                          |
| `risk_factor`         | `ForeignKey`   | `RiskFactor` (Factor de riesgo identificado).                             |
| `contribution_weight` | `DecimalField` | Grado de influencia del factor en el cálculo final (`0.00%` a `100.00%`). |

### 5. `EarlyAlert` (Alerta Temprana)

Alertas generadas automáticamente por el motor analítico o manualmente por docentes para gatillar flujos de atención y apoyo psicopedagógico.

| Campo              | Tipo Django     | Relación / Significado                                                                                        |
| :----------------- | :-------------- | :------------------------------------------------------------------------------------------------------------ |
| `enrollment`       | `ForeignKey`    | `students.Enrollment` (Matrícula del estudiante).                                                             |
| `academic_period`  | `ForeignKey`    | `academic.Academic_Period` (Periodo correspondiente).                                                         |
| `alert_type`       | `CharField(50)` | Tipo de alerta: `"low_attendance"`, `"failing_grades"`, `"behavioral"`, `"dropout_risk"`, `"socioemotional"`. |
| `description`      | `TextField`     | Justificación descriptiva del incidente o anomalía detectada.                                                 |
| `urgency_level`    | `CharField(20)` | Criticidad inicial de la alerta: `"low"`, `"medium"`, `"high"`, `"critical"`.                                 |
| `attended`         | `BooleanField`  | Flag que determina si ya recibió atención institucional (`True`/`False`).                                     |
| `attended_by_user` | `ForeignKey`    | `accounts.User` (Docente, tutor o psicólogo que atendió el caso).                                             |
| `detected_at`      | `DateTimeField` | Fecha de creación del registro.                                                                               |
| `attended_at`      | `DateTimeField` | Fecha y hora en que se ejecutó la acción de atención de la alerta.                                            |
| `response_actions` | `TextField`     | Detalle textual de las medidas y compromisos acordados al cerrar la alerta.                                   |

---

## 🚦 Motor de Cálculo de Riesgo Académico (Reglas v1)

El motor combina el estado consolidado de la matrícula escolar del periodo a través de `AcademicRiskFeatureBuilder` y decide el puntaje de riesgo final basándose en reglas semafóricas o en un clasificador supervisado ML.

### Reglas Semafóricas del Semáforo de Riesgo (Lógica del Fallback)

Si no se encuentra cargado el modelo clasificador ML en formato `risk_model.joblib`, se activa el cálculo determinista por regla de umbrales prioritarios:

1.  🔴 **Rojo (Riesgo Alto)**:
    - Tasa de asistencia inferior al **70%**.
    - **O** Promedio académico global formativo o sumativo inferior a **6.0 / 10.0**.
    - **O** Presencia de **3 o más incidentes conductuales graves** registrados.
2.  🟡 **Amarillo (Riesgo Medio)**:
    - Tasa de asistencia situada entre **70%** y **85%**.
    - **O** Promedio académico global situado entre **6.0** y **7.0 / 10.0**.
    - **O** Presencia de **5 o más incidentes conductuales leves o moderados**.
3.  🟢 **Verde (Riesgo Bajo)**:
    - Tasa de asistencia superior al **85%**.
    - **Y** Promedio académico global superior a **7.0 / 10.0**.
    - **Y** Ningún incidente conductual de carácter grave registrado.

### Algoritmo de Puntuación Numérica de Fallback (`0 - 100`)

Cuando se calcula el puntaje numérico sin modelo ML, se aplica la siguiente ponderación matricial:
$$\text{Score} = (100 - \text{Tasa de Asistencia}) \times 0.35 + (10 - \text{Nota Promedio}) \times 10 \times 0.35 + \min(\text{Incidentes} \times 10, 100) \times 0.30$$

- **Asistencia**: Peso del $35\%$.
- **Rendimiento Académico**: Peso del $35\%$.
- **Conducta/Incidentes**: Peso del $30\%$.

---

## 🔌 API Endpoints y Mapeo de Permisos (RBAC)

Todos los endpoints exigen autenticación por token JWT (`Authorization: Bearer <token>`) y están controlados de manera estricta por permisos de nivel de vista a través de la clase `HasPermission`.

| Recurso REST                                      | Método   | Acción ViewSet  | Descripción                                           | Cód. Permiso Requerido               |
| :------------------------------------------------ | :------- | :-------------- | :---------------------------------------------------- | :----------------------------------- |
| `/api/analytics/student-risk-scores/`             | `GET`    | `list`          | Listar puntajes de riesgo (paginado)                  | `analytics.view_risk_score`          |
| `/api/analytics/student-risk-scores/{id}/`        | `GET`    | `retrieve`      | Obtener detalle de un puntaje de riesgo               | `analytics.view_risk_score`          |
| `/api/analytics/feature-snapshots/`               | `GET`    | `list`          | Listar snapshots históricas (paginado)                | `analytics.view_feature_snapshot`    |
| `/api/analytics/feature-snapshots/{id}/`          | `GET`    | `retrieve`      | Obtener detalle de snapshot académica                 | `analytics.view_feature_snapshot`    |
| `/api/analytics/risk-factors/`                    | `GET`    | `list`          | Listar catálogo de factores (sin paginar)             | `analytics.view_risk_factor`         |
| `/api/analytics/risk-factors/{id}/`               | `GET`    | `retrieve`      | Ver detalle de factor de riesgo maestro               | `analytics.view_risk_factor`         |
| `/api/analytics/student-risk-factors/`            | `GET`    | `list`          | Listar factores mapeados a alumnos (paginado)         | `analytics.view_student_risk_factor` |
| `/api/analytics/student-risk-factors/{id}/`       | `GET`    | `retrieve`      | Detalle del factor de riesgo del alumno               | `analytics.view_student_risk_factor` |
| `/api/analytics/early-alerts/`                    | `GET`    | `list`          | Listar alertas tempranas registradas (paginado)       | `analytics.view_earlyalert`          |
| `/api/analytics/early-alerts/`                    | `POST`   | `create`        | Crear una nueva alerta (manual)                       | `analytics.create_earlyalert`        |
| `/api/analytics/early-alerts/{id}/`               | `PUT`    | `update`        | Actualizar los campos generales de una alerta         | `analytics.update_earlyalert`        |
| `/api/analytics/early-alerts/{id}/`               | `DELETE` | `destroy`       | Remover alerta del registro físico                    | `analytics.delete_earlyalert`        |
| `/api/analytics/early-alerts/{id}/mark_attended/` | `POST`   | `mark_attended` | Acción custom para cerrar alerta con acciones tomadas | `analytics.update_earlyalert`        |

---

## Formato de Respuestas Enriquecidas

Los serializers del módulo incluyen campos de solo lectura con los nombres relacionados a las ForeignKeys.

| Serializer                         | Campos enriquecidos                                                |
| ---------------------------------- | ------------------------------------------------------------------ |
| `StudentRiskScoreSerializer`       | `enrollment_name`, `academic_period_name`                          |
| `StudentFeatureSnapshotSerializer` | `enrollment_name`, `academic_period_name`                          |
| `StudentRiskFactorSerializer`      | `risk_factor_name` (ya existente)                                  |
| `EarlyAlertSerializer`             | `enrollment_name`, `academic_period_name`, `attended_by_user_name` |

Ejemplo de respuesta en `EarlyAlert`:

```json
{
  "id": 1,
  "enrollment": 5,
  "enrollment_name": "Juan Pérez - 5to EGB A (Activo)",
  "academic_period": 1,
  "academic_period_name": "Primer Trimestre",
  "alert_type": "ACADEMIC",
  "urgency_level": "HIGH",
  "attended_by_user": 3,
  "attended_by_user_name": "María López",
  "description": "Bajo rendimiento en Matemáticas"
}
```

---

## 🧪 Suite de Pruebas de Integración y Calidad

Para validar de manera confiable las políticas de control de acceso a nivel de fila (RLS), la denegación de accesos no autorizados (RBAC) y la integridad de las acciones específicas en bases de datos virtuales aisladas, ejecute la suite de pruebas mediante el comando recomendado del proyecto:

```bash
python manage.py test apps.analytics --settings=config.settings.test
```

> [!NOTE]
> Las pruebas en entorno aislado emplean base de datos SQLite en memoria, Celery en modo asíncrono inmediato (`task_always_eager=True`) y hashing de contraseñas de velocidad acelerada (`MD5Hasher`).
