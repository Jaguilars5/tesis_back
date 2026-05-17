# Módulo `accounts` — Gestión de Identidad y Acceso

Este módulo constituye el núcleo de seguridad del sistema, encargado de la gestión de usuarios, roles, permisos y autenticación basada en JWT.

Su diseño sigue una arquitectura desacoplada en capas (Modelos → Repositorios → Servicios → API).

---

## Estructura del Módulo

```
accounts/
├── models/         # User, Person, Role, Permission, etc.
├── repositories/   # Consultas centralizadas (ORM)
├── services/       # Lógica de negocio y cálculos
├── api/            # Serializadores y ViewSets
├── decorators/     # Decoradores de permisos
├── utils/          # Utilidades varias
└── tests/          # Pruebas unitarias y de integración
```

---

## Modelos de Datos

### Person (Persona)
Entidad base que representa a una persona física en el sistema.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document_type` | ForeignKey (DocumentType) | Tipo de documento |
| `document_number` | CharField (20) | Número de documento (único) |
| `names` | CharField (100) | Nombres |
| `last_names` | CharField (100) | Apellidos |
| `birth_date` | DateField | Fecha de nacimiento |
| `email` | EmailField | Correo electrónico |
| `phone` | CharField (15) | Teléfono |
| `active` | BooleanField | Activo |
| `created_at` | DateTimeField | Fecha de creación |
| `updated_at` | DateTimeField | Fecha de actualización |
| `deleted_at` | DateTimeField | Fecha de eliminación |

### User
Usuario del sistema (hereda de AbstractBaseUser).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `person` | OneToOneField (Person) | Persona asociada |
| `email` | EmailField | Correo (único, username) |
| `institution` | ForeignKey (Institution) | Institución |
| `active` | BooleanField | Activo |
| `is_staff` | BooleanField | Es staff admin |
| `is_superuser` | BooleanField | Es superusuario |
| `created_at` | DateTimeField | Fecha de creación |
| `updated_at` | DateTimeField | Fecha de actualización |

### Role (Rol)
Grupos de permisos asignables a usuarios.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | CharField (100) | Nombre único |
| `code` | CharField (50) | Código único |
| `description` | CharField (255) | Descripción |
| `active` | BooleanField | Activo |

### Permission (Permiso)
Permisos granulares del sistema.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `code` | CharField (100) | Código único (formato: `modulo.accion`) |
| `module` | CharField (50) | Módulo asociado |
| `description` | CharField (255) | Descripción |

### UserRole (Rol de Usuario)
Asociación usuario-rol con fecha de expiración opcional.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `user` | ForeignKey (User) | Usuario |
| `role` | ForeignKey (Role) | Rol |
| `assigned_at` | DateTimeField | Fecha de asignación |
| `expires_at` | DateTimeField | Fecha de expiración |

### RolePermission (Permiso de Rol)
Asociación rol-permiso.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `role` | ForeignKey (Role) | Rol |
| `permission` | ForeignKey (Permission) | Permiso |

### UserPermission (Permiso de Usuario)
Overrides individuales de permisos por usuario.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `user` | ForeignKey (User) | Usuario |
| `permission` | ForeignKey (Permission) | Permiso |
| `granted` | BooleanField | Otorgado (True) o Revocado (False) |
| `reason` | TextField | Razón del cambio |
| `expires_at` | DateTimeField | Fecha de expiración |
| `granted_by` | ForeignKey (User) | Usuario que otorgó |

---

## Capa de Servicios

### UserService
- `create_user`: Crea usuario con person asociada
- `update_user`: Actualiza datos de usuario
- `change_password`: Cambia contraseña
- `grant_permission` / `revoke_permission`: Gestión de permisos
- `has_permission`: Verifica si usuario tiene permiso

### RoleService
- `create_role`: Crea nuevo rol
- `assign_permissions_to_role`: Asigna permisos a rol
- `deactivate_role`: Desactiva rol

### PermissionService
- `create_permissions_bulk`: Creación masiva
- `list_permissions_by_module`: Lista por módulo

---

## API REST (Resumen)

### Autenticación (públicos)
- POST `/api/accounts/login/`
- POST `/api/accounts/refresh/`

### Usuarios
- GET/POST `/api/accounts/users/`
- GET/PUT/PATCH/DELETE `/api/accounts/users/{id}/`
- POST `/api/accounts/users/{id}/change-password/`
- POST `/api/accounts/users/{id}/grant-permission/`
- POST `/api/accounts/users/{id}/revoke-permission/`

### Roles
- GET/POST `/api/accounts/roles/`
- POST `/api/accounts/roles/{id}/assign-permissions/`

### Permisos
- GET `/api/accounts/permissions/`
- POST `/api/accounts/permissions/bulk-create/`

Ver documentación detallada en `accounts/api/README.md`.

---

## Seguridad

### Formato de Permisos
```
modulo.accion
```
Ejemplo: `grading.create_note`

### Endpoints públicos
- `POST /api/accounts/login/`
- `POST /api/accounts/refresh/`

### Permisos por ViewSet

| ViewSet | View | Create | Update | Delete |
|---------|------|--------|--------|--------|
| User | `accounts.view_user` | `accounts.create_user` | `accounts.update_user` | `accounts.delete_user` |
| Role | `accounts.view_role` | `accounts.create_role` | `accounts.update_role` | `accounts.delete_role` |
| Permission | `accounts.view_permission` | `accounts.create_permission` | `accounts.update_permission` | `accounts.delete_permission` |

Seedear permisos:
```bash
python manage.py seed_permissions --module accounts
```

---

## Pruebas

```bash
python manage.py test apps.accounts --settings=config.settings.test
```