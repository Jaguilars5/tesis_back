# Docs Auditor

Audita y mantiene la consistencia entre los archivos `README.md`, `STRUCTURE.md` y `api/README.md` y el código fuente real de cada módulo en `apps/`.

## Cuándo usarlo

- Después de crear, modificar o eliminar modelos, serializers, views, urls, servicios o repositorios
- Después de agregar o quitar archivos en cualquier `apps/<modulo>/`
- Cuando se detecte que la documentación no refleja el estado actual del código

## Qué verifica por cada módulo

### 1. Modelos
- Cuenta los archivos `.py` en `models/` (excluyendo `__init__.py`)
- Compara contra los listados en `README.md` y `STRUCTURE.md`
- Verifica que `models/__init__.py` exporte exactamente esos modelos
- Detecta si algún "modelo" documentado es en realidad un `TextChoices` (no un modelo real)

### 2. Serializers
- Cuenta clases `*Serializer` en `api/serializers.py` (o `api/serializers/*.py`)
- Verifica campos readonly documentados vs reales

### 3. ViewSets y Endpoints
- Cuenta ViewSets en `api/views.py`
- Compara contra los registros en `api/urls.py`
- Verifica que los endpoints listados en `README.md` coincidan con los del router

### 4. Archivos y Estructura
- Lee el árbol de `STRUCTURE.md` y verifica que cada archivo mencionado exista
- Detecta archivos reales no documentados

## Procedimiento

1. Lee los 3 archivos del módulo: `README.md`, `STRUCTURE.md`, `api/README.md`
2. Escanea todo el código del módulo (models, api, repositories, services, tests)
3. Compara y genera las secciones corregidas
4. Actualiza solo si hay discrepancias

## Formato de respuesta

Para cada módulo con discrepancias, reporta:

```
## <modulo> — Discrepancias

| Documentado | Realidad |
|---|---|
| ... | ... |
```

Y luego actualiza los archivos directamente.

## Apps a auditar

- `apps/academic`
- `apps/analytics`
- `apps/attendance`
- `apps/behavior`
- `apps/core`
- `apps/grading`
- `apps/iam`
- `apps/institutions`
- `apps/integration`
- `apps/people`
- `apps/students`
