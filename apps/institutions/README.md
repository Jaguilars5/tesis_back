# Módulo `institutions` — Gestión de Base Institucional

Este módulo constituye la base estructural del sistema, encargándose de la gestión de instituciones, sus años escolares y las aulas físicas disponibles.

Su diseño sigue una arquitectura desacoplada en capas (Modelos → Repositorios → Servicios → API), garantizando la integridad de los datos y validaciones de negocio centralizadas.

---

## Estructura del Módulo

```
institutions/
├── models/         # Entidades de datos
├── repositories/   # Consultas centralizadas (ORM)
├── services/       # Lógica de negocio y orquestación
├── api/            # Serializadores y controladores
└── tests/          # Pruebas unitarias y de integración
```

---

## Modelos de Datos

### Institution (Institución)
Entidad principal que representa a una unidad educativa.

| Campo | Tipo | Verbose Name |
| :--- | :--- | :--- |
| `name` | CharField (255) | Nombre de la Institución |
| `code` | CharField (100) | Código |
| `address` | CharField (255) | Dirección |
| `city` | CharField (100) | Ciudad |
| `active` | BooleanField | Activo |
| `created_at` | DateTimeField | Fecha de Creación |
| `updated_at` | DateTimeField | Fecha de Actualización |

### School_Year (Año Escolar)
Períodos de vigencia académica para una institución.

| Campo | Tipo | Verbose Name |
| :--- | :--- | :--- |
| `institution` | ForeignKey (Institution) | Institución |
| `name` | CharField (255) | Nombre del Año Escolar |
| `start_date` | DateField | Fecha de Inicio |
| `end_date` | DateField | Fecha de Fin |
| `active` | BooleanField | Activo |
| `created_at` | DateTimeField | Fecha de Creación |
| `updated_at` | DateTimeField | Fecha de Actualización |

### Classroom (Salón)
Espacios físicos destinados a la enseñanza.

| Campo | Tipo | Verbose Name |
| :--- | :--- | :--- |
| `institution` | ForeignKey (Institution) | Institución |
| `name` | CharField (100) | Nombre del Salón |
| `room_type` | CharField (50) | Tipo de Sala |
| `capacity` | IntegerField | Capacidad |
| `active` | BooleanField | Activo |

---

## Capa de Servicios

### InstitutionService (Orquestador)

- `create_institution`: Registra una nueva unidad educativa validando que el código institucional sea único en el sistema.
- `update_institution`: Permite modificar la información básica de la institución (nombre, dirección, etc.).
- `get_institution_details`: Retorna un objeto consolidado que incluye la institución, todos sus años escolares registrados y sus aulas físicas.
- `create_school_year`: Crea un nuevo período escolar validando que no existan traslapes de fechas con años ya existentes para la misma institución.
- `get_current_school_year`: Identifica automáticamente el año escolar activo comparando la fecha actual con los rangos de inicio y fin registrados.
- `create_classroom`: Registra un aula física validando que su capacidad de alumnos sea positiva.
- `get_available_classrooms`: Lista las aulas activas de una institución, permitiendo filtrar por una capacidad mínima requerida.
- `deactivate_school_year`: Realiza el borrado lógico de un año escolar para que no sea seleccionable en nuevos procesos.

---

## API REST (Resumen)

El módulo utiliza un patrón de endpoints basados en acciones POST para garantizar la consistencia en el manejo de payloads complejos.

### Instituciones
- POST `/api/institutions/institution/list/`
- POST `/api/institutions/institution/get/`
- POST `/api/institutions/institution/add/`
- POST `/api/institutions/institution/update/`
- POST `/api/institutions/institution/soft-delete/`

---

## Seguridad

Header requerido:

```
Authorization: Bearer <token>
```

---

## Pruebas

```
python manage.py test apps.institutions
```

---

## Validaciones Críticas

1.  **Conflicto de Fechas**: No se permite crear años escolares cuyos rangos de fecha se traslapen dentro de la misma institución.
2.  **Capacidad**: Las aulas deben tener una capacidad mayor a cero para ser válidas.
3.  **Códigos Únicos**: El código institucional es mandatorio y no puede repetirse en el sistema.
