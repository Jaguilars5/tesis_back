# Módulo `accounts` — Gestión de Identidad y Acceso

Este módulo constituye el núcleo de seguridad y gestión de identidad del sistema. Se encarga de la administración de personas, usuarios, roles, asignaciones y permisos granulares, además de proveer autenticación y rotación de tokens mediante JWT.

Su diseño implementa estrictamente una arquitectura en capas desacopladas:
```
Models (Estructura de Datos) ➔ Repositories (Acceso a Datos/Consultas ORM) ➔ Services (Lógica de Negocio) ➔ API (Serializadores, ViewSets, Filtros y Rutas)
```

---

## Estructura del Módulo

El módulo se organiza físicamente en la siguiente estructura de archivos y directorios:

```
apps/accounts/
├── api/
│   ├── filters.py          # Filtros avanzados de búsqueda para DRF
│   ├── serializers.py      # Transformación y validación de esquemas JSON (Login, User, Role, Permission)
│   ├── urls.py             # Enrutador RESTful para los ViewSets del módulo
│   └── views.py            # Controladores ViewSet y vistas JWT (TokenObtain, TokenRefresh)
├── decorators/
│   └── __init__.py         # Decoradores de seguridad y control de acceso
├── management/
│   └── commands/
│       └── seed_permissions.py # Inicializador idempotente de permisos del sistema en la BD
├── middleware/
│   └── __init__.py         # Middlewares específicos de seguridad de cuentas
├── models/
│   ├── __init__.py         # Punto de entrada y exportación unificada de entidades
│   ├── permission.py       # Modelo granular de definición de permisos
│   ├── person.py           # Modelo base de datos demográficos y personales
│   ├── role.py             # Modelo de agrupación de permisos en roles
│   ├── role_permission.py  # Modelo intermedio explícito para asociación Rol-Permiso
│   ├── user.py             # Modelo personalizado de usuario con JWT y lógica de validación
│   └── user_role.py        # Modelo intermedio explícito para asignación Usuario-Rol
├── repositories/
│   ├── __init__.py         # Exportación unificada de repositorios
│   ├── permission_repo.py  # Consultas de acceso a datos para permisos
│   ├── person_repo.py      # Consultas de acceso a datos para personas
│   ├── role_repo.py        # Consultas de acceso a datos para roles
│   └── user_repo.py        # Consultas de acceso a datos para usuarios
├── services/
│   ├── __init__.py         # Exportación unificada de servicios
│   ├── permission_service.py # Lógica de negocio y creación de permisos
│   ├── person_service.py   # Lógica coordinada de creación persona/usuario/estudiante
│   ├── role_service.py     # Lógica de asignación de permisos y gestión de roles
│   └── user_service.py     # Lógica de creación de cuentas, cambio de contraseña y validación de permisos
├── tests/
│   ├── test_api.py         # Pruebas de integración HTTP y control de acceso
│   ├── test_models.py      # Pruebas unitarias de integridad de la base de datos
│   ├── test_person_user.py # Pruebas de integración de flujos Persona-Usuario-Estudiante
│   ├── test_seed_permissions.py # Pruebas del comando de seed de permisos
│   └── test_services.py    # Pruebas unitarias sobre la lógica de negocio en servicios
├── utils/
│   └── __init__.py         # Funciones y clases auxiliares
├── admin.py                # Configuración de interfaces en Django Admin
├── apps.py                 # Inicialización y configuración interna de la app Django
└── README.md               # Documentación oficial del módulo (Este documento)
```

---

## Modelos de Datos (Database Schema)

El módulo define e implementa 6 entidades principales en la base de datos. Ninguna consulta directa al ORM de estos modelos se ejecuta en la capa de APIs o de Servicios; todas son encapsuladas en sus respectivos Repositories.

### 1. Person (Persona)
Representa la información física y demográfica del individuo. Es la entidad base para estudiantes, docentes y representantes.

| Campo | Tipo Django | Atributos clave | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `AutoField` | Primary Key | Identificador autoincremental de la persona. |
| `document_type` | `ForeignKey` | `on_delete=models.PROTECT`, nullable | Tipo de documento de identidad (relacionado con `institutions.DocumentType`). |
| `document_number` | `CharField(20)` | `unique=True` | Número de documento único de identidad de la persona. |
| `names` | `CharField(100)` | Obligatorio | Nombres de la persona. |
| `last_names` | `CharField(100)` | Obligatorio | Apellidos de la persona. |
| `birth_date` | `DateField` | Nullable, Blank | Fecha de nacimiento de la persona. |
| `email` | `EmailField` | Blank | Dirección de correo electrónico de la persona. |
| `phone` | `CharField(15)` | Blank | Número de teléfono de contacto. |
| `active` | `BooleanField` | `default=True` | Indica si la persona se encuentra activa en el sistema. |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Fecha y hora de creación del registro. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Fecha y hora de la última actualización. |

### 2. User (Usuario)
Hereda de `AbstractBaseUser` y representa las credenciales de ingreso y estado de autenticación en la plataforma.

| Campo | Tipo Django | Atributos clave | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `AutoField` | Primary Key | Identificador autoincremental del usuario. |
| `person` | `OneToOneField` | `on_delete=models.CASCADE`, nullable | Relación uno a uno con la entidad física `Person`. |
| `email` | `EmailField` | `unique=True` | Dirección de correo utilizada como credencial de inicio de sesión (`username`). |
| `password` | `CharField(128)` | Cifrado PBKDF2 | Contraseña hash cifrada del usuario. |
| `user_type` | `CharField(20)` | Choices, nullable, blank | Clasificación base: `ESTUDIANTE`, `DOCENTE`, `ADMIN`, `REPRESENTANTE`. |
| `active` | `BooleanField` | `default=True` | Indica si la cuenta se encuentra habilitada para autenticación. |
| `is_staff` | `BooleanField` | `default=False` | Permite el acceso a la consola de administración estándar de Django. |
| `is_superuser` | `BooleanField` | `default=False` | Otorga bypass inmediato de toda verificación de permisos del sistema. |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Fecha y hora de creación de la cuenta. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Fecha y hora de la última modificación. |

### 3. Role (Rol)
Representa agrupaciones de competencias y facultades operacionales dentro del sistema académico.

| Campo | Tipo Django | Atributos clave | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `AutoField` | Primary Key | Identificador del rol. |
| `name` | `CharField(100)` | `unique=True` | Nombre identificador legible (ej. "Administrador de Notas"). |
| `code` | `CharField(50)` | `unique=True`, nullable | Código único de referencia del rol (ej. `DOCENTE`, `ADMIN`). |
| `description` | `CharField(255)` | Blank | Explicación detallada del propósito y alcance del rol. |
| `active` | `BooleanField` | `default=True` | Determina si el rol puede seguir siendo asignado a nuevos usuarios. |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Fecha de creación del rol. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Fecha de última edición. |

### 4. Permission (Permiso Granular)
Entidad de control técnico que define acciones específicas en formato jerárquico.

| Campo | Tipo Django | Atributos clave | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `AutoField` | Primary Key | Identificador del permiso. |
| `code` | `CharField(100)` | `unique=True` | Identificador estructurado en formato `<app_label>.<action>` (ej. `grading.create_note`). |
| `description` | `CharField(255)` | Blank | Descripción detallada de lo que este permiso faculta hacer en el sistema. |
| `module` | `CharField(50)` | Blank | Módulo de agrupación para listados (ej. `grading`, `academic`). |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Fecha de creación del permiso en base de datos. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Fecha de última edición. |

### 5. UserRole (Roles de Usuario)
Asociación intermedia explícita que vincula un usuario a uno o más roles del sistema.

| Campo | Tipo Django | Atributos clave | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `AutoField` | Primary Key | Identificador autoincremental de la asociación. |
| `user` | `ForeignKey(User)` | `on_delete=models.CASCADE` | Relación con el usuario. |
| `role` | `ForeignKey(Role)` | `on_delete=models.CASCADE` | Relación con el rol. |
| `assigned_at` | `DateTimeField` | `auto_now_add=True` | Marca temporal de cuándo se le otorgó el rol. |
| `expires_at` | `DateTimeField` | Nullable, Blank | Fecha y hora límite opcional en la que esta asignación expira automáticamente. |

### 6. RolePermission (Permisos del Rol)
Asociación intermedia explícita que vincula roles con sus respectivos permisos granulares.

| Campo | Tipo Django | Atributos clave | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `AutoField` | Primary Key | Identificador de la asociación. |
| `role` | `ForeignKey(Role)` | `on_delete=models.CASCADE` | Relación con el rol. |
| `permission` | `ForeignKey(Permission)` | `on_delete=models.CASCADE` | Relación con el permiso granular concedido al rol. |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Marca temporal de la asignación del permiso al rol. |

---

## Capa de Servicios (Business Logic)

La lógica de negocio se procesa enteramente en los servicios. Los ViewSets invocan métodos estructurados que garantizan consistencia transaccional y validaciones.

### `UserService`
Orquesta la administración de cuentas de usuario del sistema.
*   `create_user(document_number, names, last_names, email, password, role_id)`: Registra una nueva persona física en el sistema con su correspondiente usuario y asignación inicial de rol dentro de una transacción. Lanza `ValueError` si el correo o documento de identidad ya están registrados.
*   `get_user(user_id)`: Retorna una instancia de usuario por su PK.
*   `get_user_by_email(email)`: Retorna un usuario por su correo electrónico.
*   `list_users()`: Recupera todos los usuarios activos ordenados por email.
*   `list_users_by_role(role_id)`: Retorna listado de usuarios que poseen asignado un rol específico.
*   `update_user(user_id, **kwargs)`: Actualiza propiedades editables del usuario (ej. email, active) validando unicidad de emails.
*   `change_password(user_id, new_password)`: Realiza el cambio seguro y actualización de contraseña de un usuario mediante cifrado hash directo.
*   `deactivate_user(user_id)`: Desactiva un usuario (soft-delete lógico en la cuenta).
*   `has_permission(user_id, permission_code)`: Retorna `True` si el usuario tiene el permiso especificado asignado en alguno de sus roles activos (o si es superusuario).
*   `get_user_permissions(user_id)`: Retorna el conjunto plano (`set`) de códigos de permisos válidos del usuario.
*   `search_users(query_string)`: Búsqueda rápida de usuarios en base a nombres, apellidos o email.

### `RoleService`
Administra el ciclo de vida de los roles y la asignación masiva de facultades.
*   `create_role(name, description, active=True)`: Crea e inicializa un nuevo rol. Valida duplicados de nombre.
*   `add_permission_to_role(role_id, permission_code)`: Asocia un permiso individual a un rol.
*   `remove_permission_from_role(role_id, permission_code)`: Desvincula un permiso individual de un rol.
*   `assign_permissions_to_role(role_id, permission_codes)`: Reemplaza completamente los permisos asignados a un rol con una nueva lista de códigos mediante transacción atómica.
*   `get_role_permissions(role_id)`: Lista los registros de permisos asignados a un rol.

### `PermissionService`
Administra el diccionario base de permisos granulares del sistema.
*   `create_permission(code, description, module)`: Registra un nuevo permiso en BD verificando unicidad de código jerárquico.
*   `create_permissions_bulk(permission_list)`: Permite la carga masiva transaccional de permisos iniciales del sistema.
*   `get_permission(permission_id)` / `get_permission_by_code(code)`: Consultas de coincidencia exacta.
*   `list_permissions()`: Retorna todos los permisos indexados en el sistema académico.
*   `list_permissions_by_module(module)`: Retorna permisos de un módulo particular (ej. `grading`).
*   `delete_permission(permission_id)`: Elimina un permiso base del sistema. Lanza una excepción si se encuentra asignado a algún rol activo en base a integridad referencial.

### `PersonService`
Provee métodos estáticos transversales para agilizar flujos de enrolamiento integrado:
*   `create_person_with_user(person_data, password)`: Crea una persona e inicializa su respectivo perfil de usuario en BD.
*   `create_person_with_student(person_data, student_code=None)`: Crea una persona física y su registro de entidad estudiante en el módulo `students` asociando o autogenerando un código único estudiantil `EST-XXXX`.
*   `search_person(names=None, email=None)`: Búsqueda granular y flexible de personas en base a parámetros demográficos.

---

## API Contract (REST API)

Todas las respuestas del módulo implementan de forma estricta la estructura estandarizada `StandardResponseRenderer` en el formato `{"ok": bool, "data": ..., "msg": "..."}`.

### Rutas de Autenticación (Públicas)
*   `POST /api/accounts/login/`
    *   **Propósito**: Autenticación y obtención de tokens JWT.
    *   **Entrada**: `{"email": "user@example.com", "password": "..."}`
    *   **Respuesta**: Contiene tokens `access`, `refresh` y el diccionario completo estructurado de `user` con datos personales, rol actual y su set completo de permisos.
*   `POST /api/accounts/refresh/`
    *   **Propósito**: Renovación de token de sesión y rotación JWT.
    *   **Entrada**: `{"refresh": "..."}`
    *   **Respuesta**: Entrega un nuevo token de acceso `access`, junto a la actualización del perfil de usuario y permisos en sesión.

### Rutas Protegidas (JWT Bearer Token requerido)

| Recurso / Acción | Método HTTP | Ruta de Endpoint | Permiso Requerido | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **Listar Usuarios** | `GET` | `/api/accounts/users/` | `accounts.view_user` | Recupera listado de usuarios con soporte de filtros. |
| **Crear Usuario** | `POST` | `/api/accounts/users/` | `accounts.create_user` | Registra e inicializa una cuenta (Persona + Usuario + Rol). |
| **Detalle de Usuario** | `GET` | `/api/accounts/users/{id}/` | `accounts.view_user` | Obtiene el detalle estructurado de una cuenta de usuario. |
| **Actualizar Usuario** | `PUT` / `PATCH` | `/api/accounts/users/{id}/` | `accounts.update_user` | Modifica datos editables del usuario. |
| **Eliminar Usuario** | `DELETE` | `/api/accounts/users/{id}/` | `accounts.delete_user` | Realiza desactivación lógica (`active=False`) de la cuenta. |
| **Cambiar Contraseña** | `POST` | `/api/accounts/users/{id}/change-password/` | `accounts.update_user` | Cambia la contraseña del usuario. Entrada: `{"new_password": "..."}`. |
| **Listar Permisos de User** | `GET` | `/api/accounts/users/{id}/permissions/` | `accounts.view_user` | Retorna el listado de códigos de permisos asignados al usuario. |
| **Búsqueda Avanzada Users** | `GET` | `/api/accounts/users/search/` | `accounts.view_user` | Búsqueda por query params `q` de coincidencia de texto. |
| **Listar Roles** | `GET` | `/api/accounts/roles/` | `accounts.view_role` | Recupera roles registrados y configuraciones. |
| **Crear Rol** | `POST` | `/api/accounts/roles/` | `accounts.create_role` | Crea e inicializa un nuevo rol. |
| **Detalle de Rol** | `GET` | `/api/accounts/roles/{id}/` | `accounts.view_role` | Recupera el detalle de un rol con su lista completa de permisos asociados. |
| **Modificar Rol** | `PUT` / `PATCH` | `/api/accounts/roles/{id}/` | `accounts.update_role` | Modifica metadatos del rol (nombre, descripción, estado). |
| **Eliminar Rol** | `DELETE` | `/api/accounts/roles/{id}/` | `accounts.delete_role` | Elimina el rol del sistema. |
| **Asignar Permisos a Rol** | `POST` | `/api/accounts/roles/{id}/assign-permissions/` | `accounts.update_role` | Reemplazo atómico masivo de permisos del rol. Entrada: `{"permission_codes": [...]}`. |
| **Vincular Permiso a Rol** | `POST` | `/api/accounts/roles/{id}/add-permission/` | `accounts.update_role` | Agrega un permiso único a un rol. Entrada: `{"permission_code": "..."}`. |
| **Remover Permiso de Rol** | `POST` | `/api/accounts/roles/{id}/remove-permission/` | `accounts.update_role` | Remueve un permiso de un rol. Entrada: `{"permission_code": "..."}`. |
| **Listar Permisos Base** | `GET` | `/api/accounts/permissions/` | `accounts.view_permission` | Recupera catálogo de permisos del sistema académico. |
| **Crear Permiso** | `POST` | `/api/accounts/permissions/` | `accounts.create_permission` | Crea un permiso individual. |
| **Actualizar Permiso** | `PUT` / `PATCH` | `/api/accounts/permissions/{id}/` | `accounts.update_permission` | Modifica metadatos de un permiso existente. |
| **Eliminar Permiso** | `DELETE` | `/api/accounts/permissions/{id}/` | `accounts.delete_permission` | Elimina el permiso (si no tiene relaciones de roles activas). |
| **Crear Permisos en Bloque**| `POST` | `/api/accounts/permissions/bulk-create/` | `accounts.create_permission` | Carga de catálogo en bloque. Entrada: `{"permissions": [...]}`. |
| **Permisos por Módulo** | `GET` | `/api/accounts/permissions/by_module/` | `accounts.view_permission` | Filtra permisos pasando parámetro de consulta `?module=nombre`. |
| **Listar Personas** | `GET` | `/api/accounts/persons/` | `accounts.view_person` | Listado general de personas del sistema. |
| **Detalle de Persona** | `GET` | `/api/accounts/persons/{id}/` | `accounts.view_person` | Detalle específico demográfico de una persona física. |

---

## Seguridad y Control de Acceso

1.  **Omisión de Permisos**: Los usuarios con la bandera `is_superuser=True` omiten automáticamente cualquier validación de código de permiso jerárquico (`has_perm` retorna de inmediato `True`).
2.  **Mecanismo de Verificación**: Los ViewSets de DRF aplican `IsAuthenticated` junto a la clase personalizada `HasPermission` de `apps.core.api.permissions`. Dicha clase mapea el nombre de la acción invocada (ej. `list`, `create`, `destroy`) a su respectivo código en la variable declarativa `action_permissions` del ViewSet.
3.  **Bypass de Base de Datos para Superusuarios**: El acceso a base de datos de administración inicial del sistema (Django admin) es controlado directamente mediante la propiedad `is_staff` sobre el modelo de usuario.

---

## Estado de Pruebas y Cobertura (Testing Status)

El módulo posee un robusto conjunto de **66 pruebas unitarias y de integración** distribuidas en la carpeta `tests/`. Todas las pruebas pasan satisfactoriamente bajo el motor SQLite configurado para entornos de pruebas (`--settings=config.settings.test`).

### Escenarios Cubiertos
*   **Pruebas de Modelos (`test_models.py`, `test_person_user.py`)**: Integridad física del modelo `Person`, unicidad en base a índice del DNI, verificación de comportamientos estandarizados de cadenas (`__str__`), flujos de creación integrada transaccional y validación de tipos.
*   **Pruebas de Lógica de Servicios (`test_services.py`, `test_person_user.py`)**: Aislamiento de validaciones de negocio (duplicados de email, existencia de roles al enrolar), flujos de cambio de clave hash con `check_password`, asignación y sustitución masiva de permisos en roles mediante transacciones SQL.
*   **Pruebas de Integración y Endpoints de API (`test_api.py`, `test_person_user.py`, `test_api_gaps.py`)**: Peticiones de login exitosas, renovación de tokens JWT, creación de usuarios mediante API, consultas demográficas e integridad de las respuestas HTTP (200, 201, 400).
*   **Control de Accesos Basado en Roles y Permisos (RBAC) (`test_api_gaps.py`)**: Pruebas explícitas negativas y positivas que garantizan que usuarios limitados reciban `403 Forbidden` al invocar acciones no asignadas y `200 OK`/`201 Created` al recibir dinámicamente dichos permisos.
*   **Pruebas sobre Capa de Filtros Avanzados (`test_api_gaps.py`)**: Cobertura completa del filtrado por query params (`UserFilter`, `RoleFilter`, `PermissionFilter`) evaluando active status, role_id, dni y filtrados por módulo de permisos (iexact).
*   **Pruebas de Integración para `PersonViewSet` (`test_api_gaps.py`)**: Pruebas detalladas que verifican que el endpoint `/api/accounts/persons/` es puramente de lectura (`ReadOnlyModelViewSet`), impidiendo escrituras no autorizadas (`POST`, `PUT`, `DELETE`).