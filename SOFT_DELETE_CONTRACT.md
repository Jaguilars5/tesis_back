# Contrato de Soft-Delete — Institutions API

Cambios realizados en el backend para unificar el patrón de desactivación
con confirmación previa y cascada sobre entidades hijas.

---

## Endpoint común

```
POST /api/institutions/{entity}/{id}/soft-delete/
Content-Type: application/json
```

Todas las entidades de `institutions` exponen este endpoint vía
`SoftDeleteModelMixin` (heredado de `BaseInstitutionsViewSet`).

---

## Comportamiento general

### 1. Sin confirmación

**Request:**
```http
POST /api/institutions/{entity}/{id}/soft-delete/
```

**Response (200) — hay hijos activos:**
```json
{
  "ok": true,
  "data": {
    "requires_confirmation": true,
    "affected_records": 5,
    "message": "Esta acción desactivará 3 secciones, 2 períodos académicos relacionados",
    "id": 1,
    "is_active": true
  }
}
```

**Response (200) — sin hijos activos (se desactiva directamente):**
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "is_active": false,
    "deactivated_records": 0
  }
}
```

### 2. Con confirmación

**Request:**
```http
POST /api/institutions/{entity}/{id}/soft-delete/
Content-Type: application/json

{ "confirm": true }
```

**Response (200):**
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "is_active": false,
    "deactivated_records": 5
  }
}
```

---

## Entidades y cascada

### SchoolYear

| Ruta | Método |
|------|--------|
| `DELETE /api/institutions/school-year/{id}/` | **Hard-delete** (elimina registro) |
| `POST /api/institutions/school-year/{id}/soft-delete/` | Desactiva + cascada |

**Cascada:**
| Tipo | Cantidad en mensaje |
|------|--------------------|
| Secciones | `secciones` |
| Ofertas de materias | `ofertas de materias` |
| Períodos académicos | `períodos académicos` |

### AcademicLevel

| Ruta | Método |
|------|--------|
| `DELETE /api/institutions/academic-levels/{id}/` | **Hard-delete** |
| `POST /api/institutions/academic-levels/{id}/soft-delete/` | Desactiva + cascada |

**Cascada:**
| Tipo | Cantidad en mensaje |
|------|--------------------|
| Subniveles | `subniveles` |
| Grados | `grados` |
| Secciones | `secciones` |
| Ofertas de materias | `ofertas de materias` |
| Configuraciones académicas | `configuraciones académicas` |
| Escalas cualitativas | `escalas cualitativas` |

### AcademicSublevel

| Ruta | Método |
|------|--------|
| `DELETE /api/institutions/academic-sublevel/{id}/` | **Hard-delete** |
| `POST /api/institutions/academic-sublevel/{id}/soft-delete/` | Desactiva + cascada |

**Cascada:**
| Tipo | Cantidad en mensaje |
|------|--------------------|
| Grados | `grados` |
| Secciones | `secciones` |
| Ofertas de materias | `ofertas de materias` |
| Configuraciones académicas | `configuraciones académicas` |
| Escalas cualitativas | `escalas cualitativas` |

### AcademicGrade

| Ruta | Método |
|------|--------|
| `DELETE /api/institutions/academic-grades/{id}/` | **Hard-delete** |
| `POST /api/institutions/academic-grades/{id}/soft-delete/` | Desactiva + cascada |

**Cascada:**
| Tipo | Cantidad en mensaje |
|------|--------------------|
| Secciones | `secciones` |
| Ofertas de materias | `ofertas de materias` |
| Configuraciones académicas | `configuraciones académicas` |

### Section

| Ruta | Método |
|------|--------|
| `DELETE /api/institutions/section/{id}/` | **Hard-delete** |
| `POST /api/institutions/section/{id}/soft-delete/` | Desactiva + cascada |

**Cascada:**
| Tipo | Cantidad en mensaje |
|------|--------------------|
| Ofertas de materias | `ofertas de materias` |

---

## DELETE en SchoolYear (cambio importante)

Anteriormente `DELETE /api/institutions/school-year/{id}/` llamaba a
`deactivate_school_year()` que solo seteaba `is_active=False`. **Ahora
hace hard-delete** (elimina el registro de la BD).

Para desactivar un SchoolYear se debe usar `POST /soft-delete/`.

---

## Flujo recomendado para el frontend

```
1. Usuario hace clic en "Desactivar"
2. Frontend hace POST /soft-delete/ sin confirm
3. Backend responde:
   a. { requires_confirmation: true, affected_records: N } → mostrar modal
      con el mensaje y botón "Confirmar"
   b. { is_active: false } directamente → notificar éxito
4. Si usuario confirma → POST /soft-delete/ con { "confirm": true }
5. Backend desactiva entidad + hijos, responde { is_active: false, deactivated_records: N }
```

## Notas

- `DELETE` siempre hace hard-delete en todas las entidades
- `POST /soft-delete/` es el único endpoint para desactivación lógica
- Los mensajes de confirmación están en español (castellano)
- `affected_records` es la suma total de todos los tipos de hijos
- `deactivated_records` equivale a `affected_records` una vez ejecutada la cascada
