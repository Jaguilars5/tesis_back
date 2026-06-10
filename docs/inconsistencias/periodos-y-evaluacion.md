# Inconsistencias: Períodos Académicos y Evaluación

## 1. `parent_period` — Campo muerto

**Archivo:** `apps/academic/models/academic_period.py:18-25`

Auto-referencia FK diseñada para jerarquías del tipo:
```
SchoolYear
  └── Quimestre 1  (parent_period = null)
        ├── Parcial 1  (parent_period = Quimestre 1)
        └── Parcial 2  (parent_period = Quimestre 1)
  └── Quimestre 2  (parent_period = null)
        ├── Parcial 1  (parent_period = Quimestre 2)
        └── Parcial 2  (parent_period = Quimestre 2)
```

**Estado actual:** El campo existe en la BD pero **nunca se puebla, consulta, filtra o referencia** en:
- `academic_service.py` — `create_academic_period()` no acepta ni asigna `parent_period`
- `academic_repo.py` — ningún método query usa `parent_period` o `child_periods`
- `EvaluationBlock` — apunta directo a `AcademicPeriod`, ignora la jerarquía
- Ningún test, serializer, vista o seed lo utiliza

## 2. `is_regular_period` — Redundante con `period_type`

**Archivo:** `apps/academic/models/academic_period.py:30-32`

| `period_type.code` | `is_regular_period` |
|--------------------|---------------------|
| REGULAR            | `True`              |
| SUPLETORIO         | `False` (implícito) |
| REFUERZO           | `False` (implícito) |

`is_regular_period` es una **desnormalización** de `period_type`. Siempre se setea como `True` en seeds y tests, y ningún servicio lo cambia a `False`. No se usa como filtro en lógica de negocio.

## 3. Jerarquía inexistente: Períodos vs. EvaluationBlock

**El problema central:** En el modelo educativo ecuatoriano:
- Un **Quimestre** se divide en **2 Parciales**
- Cada **Parcial** tiene sus propios bloques de evaluación (formativa, sumativa)
- La nota del **Quimestre** = promedio de los 2 Parciales

**Implementación actual:**
```
AcademicPeriod ("Quimestre 1")
  └── EvaluationBlock (Formativa, weight=40%)
  └── EvaluationBlock (Sumativa, weight=60%)
  └── PeriodGradeSummary (único por enrollment + subject + period)
```

**Lo que debería ser:**
```
AcademicPeriod ("Quimestre 1")
  ├── AcademicPeriod ("Parcial 1", parent_period=Quimestre 1)
  │     ├── EvaluationBlock (Formativa, weight=40%)
  │     ├── EvaluationBlock (Sumativa, weight=60%)
  │     └── PeriodGradeSummary (nota del Parcial 1)
  ├── AcademicPeriod ("Parcial 2", parent_period=Quimestre 1)
  │     ├── EvaluationBlock (Formativa, weight=40%)
  │     ├── EvaluationBlock (Sumativa, weight=60%)
  │     └── PeriodGradeSummary (nota del Parcial 2)
  └── PeriodGradeSummary (promedio de Parcial 1 + Parcial 2)
```

Actualmente **no existe un modelo que represente "Parcial 1" o "Parcial 2"** como subdivisión de un período.

## 4. `PeriodGradeSummary.unique_together` — Sin espacio para sub-períodos

**Archivo:** `apps/grading/models/period_grade_summary.py:55`

```python
unique_together = ("enrollment", "subject_offering", "academic_period")
```

Solo permite **un** resumen de notas por `enrollment + subject + period`. Si se implementaran parciales como períodos hijos, cada uno generaría su propio `PeriodGradeSummary`, y el quimestre padre necesitaría uno adicional (el promedio). La constraint actual no lo impide, pero el modelo de datos no está diseñado para esta dualidad.

## 5. `calculate_period_average` — Ignora la estructura jerárquica

**Archivo:** `apps/grading/services/evaluation_service.py:43-61`

```python
blocks = academic_period.evaluation_blocks.filter(is_active=True)
```

Recorre **todos** los `EvaluationBlock` asociados directamente al `AcademicPeriod`, sin considerar si debería agregar primero por sub-períodos (parciales) y luego promediar. Si se implementaran parciales, esta función necesitaría:
- Detectar si el período tiene hijos (`child_periods`)
- Si tiene hijos: calcular promedio de los hijos
- Si no tiene hijos: calcular promedio directo de bloques (comportamiento actual)

## 6. Propuesta de solución: Tabla intermedia

En lugar de usar `parent_period` (que mezcla la jerarquía en el mismo modelo), la opción más limpia sería una tabla extra:

```python
class PeriodDivision(TimeStampedModel):
    """Subdivisión de un período académico (Parcial 1, Parcial 2, etc.)"""
    academic_period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE, related_name="divisions")
    code = models.CharField(max_length=20)  # "PARCIAL_1", "PARCIAL_2"
    name = models.CharField(max_length=80)  # "Parcial 1", "Parcial 2"
    order = models.PositiveSmallIntegerField()  # 1, 2
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # 50%, 50%
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("academic_period", "code")
        ordering = ["academic_period", "order"]
```

Y `EvaluationBlock.academic_period` pasaría a apuntar a `PeriodDivision` en lugar de `AcademicPeriod`:

```python
# En EvaluationBlock:
period_division = models.ForeignKey(PeriodDivision, on_delete=models.CASCADE, related_name="evaluation_blocks")
```

**Ventajas:**
- Separa la jerarquía conceptual (Quimestre) de la subdivisión operativa (Parciales)
- Cada parcial tiene sus propios bloques con sus propios pesos
- `PeriodGradeSummary` se genera por `PeriodDivision` (cada parcial tiene su nota)
- El cálculo de nota del `AcademicPeriod` padre promedia las notas de sus `PeriodDivision`
- No contamina `AcademicPeriod` con lógica de subdivisión

**Alternativa:** Usar `parent_period` + un `PeriodType.PARCIAL`, pero entonces `EvaluationBlock` necesitaría un campo extra o la lógica de cálculo sería más compleja (detectar si el período es hoja o nodo en el árbol).

## Resumen de acciones pendientes

| # | Problema | Impacto | Prioridad |
|---|----------|---------|-----------|
| 1 | `parent_period` nunca se usa | Bajo (campo muerto) | Limpieza |
| 2 | `is_regular_period` redundante | Bajo (datos inconsistentes potenciales) | Limpieza |
| 3 | No existe modelo para Parcial 1 / Parcial 2 | **Alto** (brecha funcional con el dominio educativo) | Funcional |
| 4 | `calculate_period_average` no soporta jerarquía | Medio (cálculo incorrecto si se implementan parciales) | Funcional |
| 5 | `unique_together` en `PeriodGradeSummary` no contempla sub-períodos | Medio (requiere migración si se agrega `PeriodDivision`) | Técnico |
