# Modelo de Riesgo Academico

## Definicion

El riesgo academico general es el nivel estimado de vulnerabilidad de un
estudiante frente al incumplimiento de los objetivos escolares del periodo si no
recibe intervencion. Integra asistencia, calificaciones, conducta y contexto en
un semaforo institucional:

| Puntaje | Nivel | Uso |
| --- | --- | --- |
| 0-39.99 | verde | Seguimiento regular |
| 40-69.99 | amarillo | Monitoreo y apoyo preventivo |
| 70-100 | rojo | Intervencion prioritaria |

Este indicador puede apoyar el analisis preventivo de desercion porque resume
seniales asociadas al abandono escolar, como bajo rendimiento, inasistencia,
repitencia o problemas de adaptacion. No predice desercion directamente salvo
que exista un target historico explicito de abandono.

## Motores del Riesgo General

El sistema permite dos motores para el mismo constructo: riesgo academico
general institucional.

### Motor de reglas

Calcula un puntaje 0-100 con pesos y umbrales configurables:

```python
riesgo_conducta = min(100, leves*5 + moderadas*10 + graves*25)
riesgo_asistencia = 100 - porcentaje_asistencia
riesgo_calificaciones = min(
    100,
    ((10 - promedio_actual) / 10 * 100) + materias_reprobadas * 15,
)

score = (
    riesgo_conducta * peso_conducta
    + riesgo_asistencia * peso_asistencia
    + riesgo_calificaciones * peso_calificaciones
)
```

Luego aplica reglas duras de semaforo. Por ejemplo, asistencia bajo el umbral
rojo, promedio bajo el umbral rojo o incidentes graves suficientes fuerzan el
nivel rojo. El score final se ajusta para quedar dentro del rango del nivel.

### Modelo ML general

El modelo general es un `RandomForestClassifier` multiclase que aprende el mismo
semaforo institucional que reglas:

- `0`: verde
- `1`: amarillo
- `2`: rojo

El target de entrenamiento se genera aplicando el motor de reglas sobre cada
`StudentFeatureSnapshot` historico. Por eso la comparativa `ML - reglas` compara
dos estimaciones del mismo riesgo, no riesgo general contra probabilidad de
reprobacion.

El artefacto `apps/analytics/ml/risk_model.joblib` guarda:

- `model_type: "general_institutional_risk"`
- `target: "rules_risk_label/rules_risk_score"`
- `features`
- `feature_importances`
- `score_class_centers`
- `rules_config`
- `training_params`
- `training_metrics`

Durante inferencia, el modelo predice probabilidades por clase y las convierte a
score 0-100 con centros de clase. El score se ajusta al rango del semaforo de la
clase predicha para mantener consistencia entre puntaje y nivel.

## Features del Modelo General

El contrato canonico de entrada vive en `apps/analytics/ml/features.py`:

```python
FEATURE_COLUMNS = [
    "attendance_rate",
    "consecutive_absences_max",
    "tardiness_count",
    "justified_absences",
    "unjustified_absences",
    "formative_avg_normalized",
    "summative_avg_normalized",
    "grade_trend_slope",
    "failing_subjects_count",
    "conduct_score",
    "severe_incidents_count",
    "family_notified_ratio",
    "prev_period_avg_grade",
    "age_grade_gap",
    "is_repeat",
    "has_special_needs",
]
```

`failing_subjects_count` se conserva como feature del modelo general porque el
target ya no es `is_failing` puro; es una senial valida dentro del riesgo
academico institucional.

## Modelos Especializados

Los modelos por materia y anual no reemplazan al riesgo general ni se comparan
directamente contra sus reglas.

| Modelo | Objetivo | Salida |
| --- | --- | --- |
| General | Riesgo academico institucional integral | Score 0-100 y semaforo |
| Por materia | Riesgo de bajo rendimiento o reprobacion en una asignatura | Probabilidad y nivel bajo/medio/alto |
| Anual | Riesgo de perdida/promocion anual | Probabilidad y nivel bajo/medio/alto |
| Desercion | Riesgo de abandono o no continuidad institucional | Probabilidad y nivel bajo/medio/alto |

El modelo de desercion se entrena como un artefacto independiente:
`apps/analytics/ml/dropout_risk_model.joblib`. Su target v1 considera abandono
cuando la matricula historica queda en estado retirado o inactivo, excluyendo
motivos que indiquen traslado, graduacion o promocion normal cuando esten
codificados en el motivo de retiro.

## Entrenamiento

```bash
python manage.py train_risk_model
```

Entrena el modelo general institucional.

```bash
python manage.py train_risk_model --subject-model
python manage.py train_risk_model --annual-model
python manage.py train_risk_model --dropout-model
```

Entrenan los modelos especializados.

El entrenamiento general reporta distribucion de clases, accuracy, F1 ponderado,
classification report y matriz de confusion. Si el artefacto general existente
no tiene `model_type: "general_institutional_risk"`, la inferencia lo rechaza y
usa el motor de reglas como fallback hasta reentrenar.

## Probador de Modelos

La pantalla de probador usa parametros manuales y no persiste resultados. Sus
tabs llaman endpoints separados:

| Tab | Endpoint | Persistencia |
| --- | --- | --- |
| General | `/student-risk-scores/simulate/` | No guarda score |
| Por materia | `/student-risk-scores/simulate_subject/` | No guarda score |
| Anual | `/student-risk-scores/simulate_annual/` | No guarda score |
| Desercion | `/student-risk-scores/simulate_dropout/` | No guarda score |

Para estudiantes reales existen endpoints predictivos especificos:
`predict_subject_risk`, `predict_annual_risk` y `predict_dropout_risk`.
