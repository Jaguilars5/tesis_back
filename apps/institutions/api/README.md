# API - Módulo Institutions

Esta API gestiona las entidades base del sistema: años escolares, niveles académicos, subniveles, grados académicos y secciones (aulas/paralelos).

---

## Formato de Respuesta Estándar

Todas las respuestas usan el formato `{"ok": bool, "data": ..., "msg": "..."}` a través de `StandardResponseRenderer`.

| Código | Descripción                          |
| ------ | ------------------------------------ |
| 200    | Éxito (listar, obtener, actualizar)  |
| 201    | Creación exitosa                     |
| 204    | Eliminación exitosa (solo `section`) |
| 400    | Error de validación/solicitud        |
| 401    | No autenticado                       |
| 403    | Sin permisos                         |
| 404    | No encontrado                        |

---

## Autenticación y Permisos

Se requiere un token JWT válido en el header de cada petición:

```
Authorization: Bearer <access_token>
```

Todos los endpoints requieren autenticación (`IsAuthenticated`) + permiso específico por acción.

### Endpoints y Permisos

| Endpoint             | GET                                   | POST                                    | PUT/PATCH                               | DELETE                                  | soft-delete                   |
| -------------------- | ------------------------------------- | --------------------------------------- | --------------------------------------- | --------------------------------------- | ----------------------------- |
| `school-year/`       | `institutions.view_school_year`       | `institutions.create_school_year`       | `institutions.update_school_year`       | `institutions.delete_school_year`¹      | —                             |
| `academic-levels/`   | `institutions.view_academic_level`    | `institutions.create_academic_level`    | `institutions.update_academic_level`    | `institutions.delete_academic_level`    | —                             |
| `academic-sublevel/` | `institutions.view_academic_sublevel` | `institutions.create_academic_sublevel` | `institutions.update_academic_sublevel` | `institutions.delete_academic_sublevel` | —                             |
| `academic-grades/`   | `institutions.view_academic_grade`    | `institutions.create_academic_grade`    | `institutions.update_academic_grade`    | `institutions.delete_academic_grade`    | —                             |
| `section/`           | `institutions.view_section`           | `institutions.create_section`           | `institutions.update_section`           | `institutions.delete_section`           | `institutions.delete_section` |

> ¹ `school-year/` **DELETE** realiza borrado lógico vía `InstitutionService.deactivate_school_year` (no elimina físicamente, desactiva con `is_active=False`). `school-year/` no tiene soft-delete.

---

## Parámetros de Consulta (Listados)

Los endpoints de listado (`GET`) aceptan los siguientes parámetros opcionales:

### `?search=`

Filtra resultados por coincidencia parcial (`icontains`) sobre el nombre del modelo
(o `parallel` en el caso de `section/`):

| Endpoint             | Busca sobre | Ejemplo          |
| -------------------- | ----------- | ---------------- |
| `school-year/`       | `name`      | `?search=2024`   |
| `academic-levels/`   | `name`      | `?search=basica` |
| `academic-sublevel/` | `name`      | `?search=bachi`  |
| `academic-grades/`   | `name`      | `?search=5to`    |
| `section/`           | `parallel`  | `?search=A`      |

### `?ordering=`

Ordena resultados por campo. Prefijo `-` para descendente:

| ViewSet                   | Campos disponibles               |
| ------------------------- | -------------------------------- |
| `SchoolYearViewSet`       | `name`, `start_date`, `end_date` |
| `AcademicLevelViewSet`    | `name`                           |
| `AcademicSublevelViewSet` | `name`, `code`                   |
| `AcademicGradeViewSet`    | `name`, `sequence_order`         |
| `SectionViewSet`          | `parallel`, `capacity`           |

### Ejemplos de uso combinado

```bash
# Años escolares: buscar "2024" y ordenar por fecha de inicio descendente
GET /api/institutions/school-year/?search=2024&ordering=-start_date

# Grados: ordenar por secuencia ascendente
GET /api/institutions/academic-grades/?ordering=sequence_order

# Secciones: filtrar paralelo "A" y ordenar por capacidad descendente
GET /api/institutions/section/?search=A&ordering=-capacity

# Subniveles: buscar "basica" y ordenar por código
GET /api/institutions/academic-sublevel/?search=basica&ordering=code
```

---

## Años Escolares (`/api/institutions/school-year/`)

Gestiona los años lectivos. **Usa servicio con validaciones**: solapamiento de fechas y coherencia inicio/fin.

**GET** `/api/institutions/school-year/` — Listar
**POST** `/api/institutions/school-year/` — Crear (vía `InstitutionService`)
**PUT** `/api/institutions/school-year/{id}/` — Actualizar (vía `InstitutionService`)
**PATCH** `/api/institutions/school-year/{id}/` — Actualización parcial (vía `InstitutionService`)
**DELETE** `/api/institutions/school-year/{id}/` — Desactivar (`is_active=False`, vía servicio)

### Listar

```bash
GET /api/institutions/school-year/?search=2024
GET /api/institutions/school-year/?ordering=-start_date
GET /api/institutions/school-year/?search=2024&ordering=name&page=1&page_size=10
```

Response:

```json
{
  "ok": true,
  "data": {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "2024-2025",
        "start_date": "2024-09-01",
        "end_date": "2025-07-31",
        "is_active": true
      }
    ]
  },
  "msg": ""
}
```

### Crear

Request:

```json
{
  "name": "2024-2025",
  "start_date": "2024-09-01",
  "end_date": "2025-07-31"
}
```

> **Validaciones:** La fecha de inicio debe ser anterior a la fecha de fin. No puede solaparse con las fechas de otro año escolar activo.

### Actualizar

**PUT** `/api/institutions/school-year/{id}/`

**PATCH** `/api/institutions/school-year/{id}/`

Request (parcial):

```json
{
  "end_date": "2025-08-31"
}
```

### Eliminar (desactivación)

**DELETE** `/api/institutions/school-year/{id}/`

No elimina el registro físicamente. Lo desactiva seteando `is_active=False` a través de `InstitutionService.deactivate_school_year`.

---

## Niveles Académicos (`/api/institutions/academic-levels/`)

Catálogo de niveles educativos (Educación General Básica, Bachillerato, etc.).

**GET** `/api/institutions/academic-levels/` — Listar
**POST** `/api/institutions/academic-levels/` — Crear
**PUT** `/api/institutions/academic-levels/{id}/` — Actualizar
**PATCH** `/api/institutions/academic-levels/{id}/` — Actualización parcial
**DELETE** `/api/institutions/academic-levels/{id}/` — Eliminar

### Listar

```bash
GET /api/institutions/academic-levels/?search=basica
GET /api/institutions/academic-levels/?ordering=name
```

Response:

```json
{
  "ok": true,
  "data": {
    "count": 3,
    "results": [
      {
        "id": 1,
        "code": "EGB",
        "name": "Educación General Básica",
        "is_active": true
      },
      {
        "id": 2,
        "code": "BGU",
        "name": "Bachillerato General Unificado",
        "is_active": true
      }
    ]
  },
  "msg": ""
}
```

### Crear

Request:

```json
{
  "code": "EGB",
  "name": "Educación General Básica"
}
```

---

## Subniveles Académicos (`/api/institutions/academic-sublevel/`)

Subdivisiones de los niveles académicos. Incluye `academic_level_name` (campo de solo lectura).

**GET** `/api/institutions/academic-sublevel/` — Listar
**POST** `/api/institutions/academic-sublevel/` — Crear
**PUT** `/api/institutions/academic-sublevel/{id}/` — Actualizar
**PATCH** `/api/institutions/academic-sublevel/{id}/` — Actualización parcial
**DELETE** `/api/institutions/academic-sublevel/{id}/` — Eliminar

### Listar

```bash
GET /api/institutions/academic-sublevel/?search=bachi
GET /api/institutions/academic-sublevel/?ordering=code
GET /api/institutions/academic-sublevel/?search=basica&ordering=code&page=2&page_size=20
```

Response:

```json
{
  "ok": true,
  "data": {
    "count": 2,
    "results": [
      {
        "id": 1,
        "academic_level": 1,
        "academic_level_name": "Educación General Básica",
        "code": "BASICA",
        "name": "Básica",
        "description": "Subnivel de Educación General Básica",
        "is_active": true
      }
    ]
  },
  "msg": ""
}
```

### Crear

Request:

```json
{
  "academic_level": 1,
  "code": "BASICA",
  "name": "Básica",
  "description": "Subnivel de Educación General Básica"
}
```

---

## Grados Académicos (`/api/institutions/academic-grades/`)

Grados o cursos dentro de un subnivel académico. Incluye `academic_level_name` (campo de solo lectura, resuelto desde `academic_sublevel.academic_level`).

**GET** `/api/institutions/academic-grades/` — Listar
**POST** `/api/institutions/academic-grades/` — Crear
**PUT** `/api/institutions/academic-grades/{id}/` — Actualizar
**PATCH** `/api/institutions/academic-grades/{id}/` — Actualización parcial
**DELETE** `/api/institutions/academic-grades/{id}/` — Eliminar

### Listar

```bash
GET /api/institutions/academic-grades/?search=8vo
GET /api/institutions/academic-grades/?ordering=sequence_order
GET /api/institutions/academic-grades/?page=1&page_size=10
```

Response:

```json
{
  "ok": true,
  "data": {
    "count": 2,
    "results": [
      {
        "id": 1,
        "code": "8VO",
        "academic_sublevel": 1,
        "academic_level_name": "Educación General Básica",
        "name": "8vo EGB",
        "sequence_order": 8,
        "is_active": true
      }
    ]
  },
  "msg": ""
}
```

### Crear

Request:

```json
{
  "code": "8VO",
  "academic_sublevel": 1,
  "name": "8vo EGB",
  "sequence_order": 8
}
```

---

## Secciones (`/api/institutions/section/`)

Aulas o paralelos asociados a un año escolar y grado académico. Incluye `school_year_name` y `academic_grade_name` como campos de solo lectura.

**GET** `/api/institutions/section/` — Listar
**POST** `/api/institutions/section/` — Crear
**PUT** `/api/institutions/section/{id}/` — Actualizar
**PATCH** `/api/institutions/section/{id}/` — Actualización parcial
**DELETE** `/api/institutions/section/{id}/` — Eliminar (físico)
**POST** `/api/institutions/section/{id}/soft-delete/` — Desactivar (borrado lógico)

### Listar

```bash
GET /api/institutions/section/?search=A
GET /api/institutions/section/?ordering=parallel
GET /api/institutions/section/?search=A&ordering=-capacity&page=1&page_size=50
```

Response:

```json
{
  "ok": true,
  "data": {
    "count": 2,
    "results": [
      {
        "id": 1,
        "code": "SEC-001",
        "school_year": 1,
        "school_year_name": "2024-2025",
        "academic_grade": 1,
        "academic_grade_name": "8vo EGB",
        "parallel": "A",
        "capacity": 30,
        "is_active": true
      }
    ]
  },
  "msg": ""
}
```

### Crear

Request:

```json
{
  "code": "SEC-001",
  "school_year": 1,
  "academic_grade": 1,
  "parallel": "A",
  "capacity": 30
}
```

### Actualizar

**PUT** `/api/institutions/section/{id}/`

**PATCH** `/api/institutions/section/{id}/`

Request (parcial):

```json
{
  "parallel": "B",
  "capacity": 35
}
```

### Eliminar

**DELETE** `/api/institutions/section/{id}/` — Elimina el registro físicamente de la base de datos.

**POST** `/api/institutions/section/{id}/soft-delete/` — Desactiva el registro (`is_active=False`).

---

## Características Comunes

### Soft Delete

Disponible en `section/` mediante `POST /api/institutions/section/{id}/soft-delete/`. Marca `is_active = False` en lugar de eliminar el registro.

El endpoint `school-year/` utiliza su propio mecanismo de desactivación: `DELETE /api/institutions/school-year/{id}/` realiza borrado lógico vía `InstitutionService.deactivate_school_year`.

### Paginación

Usa `StandardResultsSetPagination`. La respuesta paginada incluye:

```json
{
  "count": 100,
  "next": "http://...?page=2",
  "previous": null,
  "results": [...]
}
```

### Búsqueda y Ordenamiento

Todos los ViewSets de institutions soportan:

- `?search=` para filtrar por nombre del campo principal (o `parallel` en secciones)
- `?ordering=` para ordenar por campos específicos

Los parámetros pueden combinarse entre sí y con `?page=` y `?page_size=`.

---

## Notas

- No existe el modelo `Institution` en este módulo. La gestión institucional se realiza a través de `SchoolYear` (años escolares) y las demás entidades académicas.
- El patrón usado es RESTful con `DefaultRouter` (5 ViewSets registrados).
- `AcademicGrade` usa FK a `AcademicSublevel` (no directamente a `AcademicLevel`). El campo de solo lectura `academic_level_name` se resuelve como propiedad del modelo desde `academic_sublevel.academic_level.name`.
- Todos los modelos usan el campo `is_active` para control de borrado lógico.
- `AcademicLevel`, `AcademicGrade` y `Section` incluyen el campo `code` como identificador corto opcional.
