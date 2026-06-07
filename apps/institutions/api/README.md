# API - Módulo Institutions

Esta API gestiona las entidades base del sistema: años escolares, tipos de documento, niveles académicos y grados.

---

## Formato de Respuesta

Todas las peticiones siguen el formato estandarizado:

```json
{
  "ok": true,
  "data": {},
  "msg": ""
}
```

---

## Autenticación y Permisos

Header requerido:

```
Authorization: Bearer <access_token>
```

| Endpoint                | Método | Permiso                              |
| ----------------------- | ------ | ------------------------------------ |
| `school-year/`          | GET    | `institutions.view_school_year`      |
| `school-year/`          | POST   | `institutions.create_school_year`    |
| `school-year/{id}/`     | GET    | `institutions.view_school_year`      |
| `school-year/{id}/`     | PATCH  | `institutions.update_school_year`    |
| `school-year/{id}/`     | DELETE | `institutions.delete_school_year`    |
| `document-types/`       | GET    | `institutions.view_document_type`    |
| `document-types/{id}/`  | GET    | `institutions.view_document_type`    |
| `academic-levels/`      | GET    | `institutions.view_academic_level`   |
| `academic-levels/`      | POST   | `institutions.create_academic_level` |
| `academic-levels/{id}/` | GET    | `institutions.view_academic_level`   |
| `academic-levels/{id}/` | PATCH  | `institutions.update_academic_level` |
| `academic-levels/{id}/` | DELETE | `institutions.delete_academic_level` |
| `academic-grades/`      | GET    | `institutions.view_academic_grade`   |
| `academic-grades/`      | POST   | `institutions.create_academic_grade` |
| `academic-grades/{id}/` | GET    | `institutions.view_academic_grade`   |
| `academic-grades/{id}/` | PATCH  | `institutions.update_academic_grade` |
| `academic-grades/{id}/` | DELETE | `institutions.delete_academic_grade` |

---

## Años Escolares (`/api/institutions/school-year/`)

### Listar

**GET** `/api/institutions/school-year/`

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
        "active": true
      }
    ]
  },
  "msg": ""
}
```

### Crear

**POST** `/api/institutions/school-year/`

Request:

```json
{
  "name": "2024-2025",
  "start_date": "2024-09-01",
  "end_date": "2025-07-31"
}
```

### Actualizar

**PATCH** `/api/institutions/school-year/{id}/`

### Eliminar (Soft Delete)

**DELETE** `/api/institutions/school-year/{id}/`

---

## Tipos de Documento (`/api/institutions/document-types/`)

Solo lectura (ReadOnlyModelViewSet).

### Listar

**GET** `/api/institutions/document-types/`

Response:

```json
{
  "ok": true,
  "data": [
    { "id": 1, "code": "CC", "name": "Cédula de Ciudadanía" },
    { "id": 2, "code": "PAS", "name": "Pasaporte" }
  ],
  "msg": ""
}
```

---

## Niveles Académicos (`/api/institutions/academic-levels/`)

### Listar

**GET** `/api/institutions/academic-levels/`

### Crear

**POST** `/api/institutions/academic-levels/`

Request:

```json
{
  "name": "Educación General Básica",
  "active": true
}
```

---

## Grados Académicos (`/api/institutions/academic-grades/`)

### Listar

**GET** `/api/institutions/academic-grades/`

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
        "name": "8vo EGB",
        "subnivel": "ELEMENTAL",
        "sequence_order": 8,
        "active": true
      }
    ]
  },
  "msg": ""
}
```

### Crear

**POST** `/api/institutions/academic-grades/`

Request:

```json
{
  "academic_level": 1,
  "name": "8vo EGB",
  "subnivel": "ELEMENTAL",
  "sequence_order": 8
}
```

---

## Notas

- No existe el modelo `Institution` en este módulo. La gestión institucional se realiza a través de `School_Year` (años escolares).
- El patrón usado es RESTful con `DefaultRouter`, no el patrón POST-based (list/, get/, add/) que aparece en documentación antigua.
- `Section` (secciones/Paralelos) no tiene ViewSet en institutions; se gestiona a través de la matrícula del estudiante en `students`.
