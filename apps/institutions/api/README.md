# API - Módulo Institutions

Esta API gestiona las entidades base del sistema: instituciones, años escolares y aulas.

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

## Patrón de Endpoints

El módulo `institutions` utiliza un patrón de endpoints fijos basados en acciones POST.

### Instituciones (`/api/institutions/institution/`)

#### Listar
**POST** `/api/institutions/institution/list/`

Response:
```json
{
  "ok": true,
  "data": [
    {
      "id": 1,
      "name": "Colegio Nacional",
      "code": "CN-001",
      "city": "Quito"
    }
  ],
  "msg": ""
}
```

#### Obtener Detalle
**POST** `/api/institutions/institution/get/`

Request:
```json
{
  "id": 1
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "name": "Colegio Nacional",
    "code": "CN-001"
  },
  "msg": ""
}
```

#### Agregar
**POST** `/api/institutions/institution/add/`

Request:
```json
{
  "name": "Colegio Nacional",
  "code": "CN-001",
  "address": "Av. Amazonas",
  "city": "Quito"
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "name": "Colegio Nacional"
  },
  "msg": ""
}
```

#### Actualizar
**POST** `/api/institutions/institution/update/`

Request:
```json
{
  "id": 1,
  "name": "Nuevo Nombre"
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "name": "Nuevo Nombre"
  },
  "msg": ""
}
```

#### Borrado Lógico
**POST** `/api/institutions/institution/soft-delete/`

Request:
```json
{
  "id": 1
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "active": false
  },
  "msg": ""
}
```

---

## Años Escolares (`/api/institutions/school-year/`)

### Agregar Año Escolar
**POST** `/api/institutions/school-year/add/`

Request:
```json
{
  "institution": 1,
  "name": "2024-2025",
  "start_date": "2024-09-01",
  "end_date": "2025-07-31"
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "name": "2024-2025"
  },
  "msg": ""
}
```

---

## Aulas (`/api/institutions/classroom/`)

### Agregar Aula
**POST** `/api/institutions/classroom/add/`

Request:
```json
{
  "institution": 1,
  "name": "Aula 101",
  "room_type": "Aula de clase",
  "capacity": 40
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "name": "Aula 101"
  },
  "msg": ""
}
```
