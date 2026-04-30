# Módulo `accounts` — Gestión de Cuentas y Permisos

Este módulo implementa el patrón de arquitectura de **separación en capas** (models → repositories → services → api) que ya se usa en `grading` y `academic`.

## Estructura de Carpetas

```
accounts/
├── models/                    # Capa de datos (5 modelos)
│   ├── __init__.py           # Re-export de todos los modelos
│   ├── user.py               # Modelo User
│   ├── role.py               # Modelo Role
│   ├── permission.py         # Modelo Permission
│   ├── role_permission.py    # Tabla intermedia Role ↔ Permission
│   └── user_permission.py    # Excepciones de usuario
│
├── repositories/             # Capa de acceso a datos (3 repositorios)
│   ├── __init__.py
│   ├── user_repo.py          # Queries de User
│   ├── role_repo.py          # Queries de Role
│   └── permission_repo.py    # Queries de Permission
│
├── services/                 # Capa de lógica de negocio (3 servicios)
│   ├── __init__.py
│   ├── user_service.py       # Orquesta operaciones de User
│   ├── role_service.py       # Orquesta operaciones de Role
│   └── permission_service.py # Orquesta operaciones de Permission
│
├── api/                      # Capa HTTP (REST)
│   ├── __init__.py
│   ├── serializers.py        # Validadores de entrada/salida
│   ├── views.py              # ViewSets de DRF
│   ├── filters.py            # Filtros para listados
│   └── urls.py               # Rutas en router DRF
│
├── utils/                    # Funciones auxiliares
│   ├── __init__.py           # JWT, password, permission helpers
│   └── README.md             # Documentación
│
├── middleware/               # Middleware personalizado
│   ├── __init__.py           # Incluye JWTAuthMiddleware
│   ├── jwt_auth.py           # Implementación JWT
│   └── README.md             # Documentación
│
├── decorators/               # Decoradores
│   ├── __init__.py           # Incluye @require_permission
│   └── README.md             # Documentación
│
├── tests/                    # Tests (3 suites)
│   ├── __init__.py
│   ├── test_models.py        # Tests unitarios de modelos
│   ├── test_services.py      # Tests de lógica de negocio
│   └── test_api.py           # Tests de integración HTTP
│
├── admin.py                  # Panel de administración Django
├── apps.py                   # Configuración de la app
├── urls.py                   # Rutas que incluyen api/urls.py
├── README.md                 # Este archivo
└── migrations/               # Migraciones (auto-generadas)
```

## Modelos

### User

Usuario del sistema con campos:

- `dni`: Documento único
- `names`, `last_names`, `email`: Datos personales
- `password`: Almacena el hash (heredado de AbstractBaseUser)
- `role`: FK a Role (rol asignado)
- `institution`: FK a Institution (institución a la que pertenece)
- `active`: Indica si puede acceder al sistema

**Métodos útiles:**

```python
user.set_password(raw_password)       # Hashea y guarda
user.check_password(raw_password)     # Verifica contraseña
user.has_perm('codename')             # Verifica permisos (combina role + overrides)
user.get_all_permissions()            # Retorna set de codenames
```

### Role

Rol del sistema (Docente, Admin, Director, etc) que agrupa permisos.

- `name`: Nombre único
- `description`: Descripción del rol
- `active`: Si puede ser asignado a nuevos usuarios

**Métodos útiles:**

```python
role.get_all_permissions()  # Retorna Permission objects del rol
```

### Permission

Permiso atómico del sistema.

- `codename`: Identificador único (formato: `'app.action'`, ej: `'grading.create_note'`)
- `description`: Descripción legible
- `module`: Módulo asociado (grading, academic, etc)

### RolePermission
Tabla intermedia explícita que vincula Role ↔ Permission. Se accede desde Permission vía `permission_roles` y desde Role vía `role_permissions`.

### UserPermission

Excepciones a nivel de usuario:

- `granted=True`: Otorga un permiso aunque el rol no lo tenga
- `granted=False`: Revoca un permiso aunque el rol sí lo tenga
- `reason`: Campo auditable
- `expires_at`: Expiración opcional
- `granted_by`: Usuario que hizo el cambio (auditoría)

## Lógica de Permisos

Cuando verificas `user.has_perm('codename')`:

1. Si existe `UserPermission(user, permission, granted=X)`:
   - Retorna `X` (override)
2. Si no existe UserPermission:
   - Verifica si el `role` tiene el permiso
   - Hereda del role

```python
# Ejemplo
user = User.objects.get(email='juan@example.com')

# Hereda del role
user.has_perm('grading.view_notes')  # True si el role tiene ese permiso

# Override: revocar un permiso del role
UserPermission.objects.create(
    user=user,
    permission=Permission.objects.get(codename='grading.view_notes'),
    granted=False,
    reason='Usuario revocado temporalmente'
)
user.has_perm('grading.view_notes')  # Ahora False

# Override: otorgar un permiso adicional
UserPermission.objects.create(
    user=user,
    permission=Permission.objects.get(codename='admin.delete_users'),
    granted=True,
    reason='Acceso temporal para auditoría'
)
user.has_perm('admin.delete_users')  # True
```

## Repositorio (Capa de Acceso a Datos)

Centraliza queries complejas en un lugar. El service nunca hace:

```python
# ❌ INCORRECTO
User.objects.filter(...).select_related(...).annotate(...)
```

En su lugar, delega al repositorio:

```python
# ✓ CORRECTO
from apps.accounts.repositories.user_repo import UserRepository
users = UserRepository.get_by_role(role_id=1, institution_id=1)
```

### UserRepository

```python
from apps.accounts.repositories.user_repo import UserRepository

# Consultas
UserRepository.get_by_id(user_id)
UserRepository.get_by_email(email)
UserRepository.get_by_dni(dni, institution_id=None)
UserRepository.get_all_active(institution_id=None)
UserRepository.get_by_role(role_id, institution_id=None)
UserRepository.search(query_string, institution_id=None)

# Operaciones
UserRepository.create(dni, names, last_names, email, password, role, institution)
UserRepository.update(user, **kwargs)
UserRepository.delete(user)  # Soft-delete
UserRepository.bulk_create(user_list)
```

### RoleRepository

```python
from apps.accounts.repositories.role_repo import RoleRepository

RoleRepository.get_by_id(role_id)
RoleRepository.get_by_name(name)
RoleRepository.get_all_active()
RoleRepository.create(name, description="", active=True)
RoleRepository.add_permission(role, permission)
RoleRepository.remove_permission(role, permission)
RoleRepository.get_permissions(role_id)
```

### PermissionRepository

```python
from apps.accounts.repositories.permission_repo import PermissionRepository

PermissionRepository.get_by_id(permission_id)
PermissionRepository.get_by_codename(codename)
PermissionRepository.get_all()
PermissionRepository.get_by_module(module)
PermissionRepository.create(codename, description="", module="")
PermissionRepository.create_many(permission_list)
PermissionRepository.search(query_string)
```

## Service (Capa de Lógica de Negocio)

Orquesta operaciones entre repositories, modelos y tareas asíncronas. **Nunca accede directamente a `User.objects`**.

### UserService

```python
from apps.accounts.services.user_service import UserService

service = UserService()

# Crear usuario
user = service.create_user(
    dni='123456789',
    names='Juan',
    last_names='Pérez',
    email='juan@example.com',
    password='micontraseña123',
    role_id=1,
    institution_id=1
)

# Consultar
user = service.get_user(user_id)
user = service.get_user_by_email(email)
users = service.list_users(institution_id=None)

# Actualizar
service.update_user(user_id, names='Pedro', role=2)
service.change_password(user_id, 'nuevapass123')

# Permisos
service.grant_permission(user_id, 'grading.create_note', reason='Acceso temporal')
service.revoke_permission(user_id, 'grading.delete_note', reason='Revocado')
service.has_permission(user_id, 'grading.view_notes')
service.get_user_permissions(user_id)

# Búsqueda
service.search_users('juan', institution_id=1)
```

### RoleService

```python
from apps.accounts.services.role_service import RoleService

service = RoleService()

# Crear
role = service.create_role('Docente', 'Rol de docente')

# Permisos
service.add_permission_to_role(role_id, 'grading.create_note')
service.remove_permission_from_role(role_id, 'grading.delete_note')
service.assign_permissions_to_role(role_id, ['perm1', 'perm2', 'perm3'])
service.get_role_permissions(role_id)
```

### PermissionService

```python
from apps.accounts.services.permission_service import PermissionService

service = PermissionService()

# Crear
perm = service.create_permission('grading.create_note', 'Crear notas', 'grading')
service.create_permissions_bulk([
    {'codename': 'perm1', 'description': 'P1', 'module': 'test'},
    {'codename': 'perm2', 'description': 'P2', 'module': 'test'},
])

# Consultar
service.list_permissions()
service.list_permissions_by_module('grading')
```

## API REST

Todos los endpoints requieren autenticación. Usa `APIClient` en tests.

### Permissions

```
GET    /api/accounts/permissions/          # Listar
POST   /api/accounts/permissions/          # Crear
GET    /api/accounts/permissions/{id}/     # Detalle
PUT    /api/accounts/permissions/{id}/     # Actualizar
DELETE /api/accounts/permissions/{id}/     # Eliminar
POST   /api/accounts/permissions/bulk-create/  # Crear múltiples
GET    /api/accounts/permissions/by-module/?module=grading  # Por módulo
```

### Roles

```
GET    /api/accounts/roles/                 # Listar
POST   /api/accounts/roles/                 # Crear
GET    /api/accounts/roles/{id}/            # Detalle
PUT    /api/accounts/roles/{id}/            # Actualizar
DELETE /api/accounts/roles/{id}/            # Desactivar
POST   /api/accounts/roles/{id}/add-permission/         # Agregar permiso
POST   /api/accounts/roles/{id}/remove-permission/      # Remover permiso
POST   /api/accounts/roles/{id}/assign-permissions/     # Asignar múltiples
```

### Users

```
GET    /api/accounts/users/                 # Listar
POST   /api/accounts/users/                 # Crear
GET    /api/accounts/users/{id}/            # Detalle
PUT    /api/accounts/users/{id}/            # Actualizar
DELETE /api/accounts/users/{id}/            # Desactivar
POST   /api/accounts/users/{id}/change-password/        # Cambiar password
POST   /api/accounts/users/{id}/grant-permission/       # Otorgar permiso
POST   /api/accounts/users/{id}/revoke-permission/      # Revocar permiso
GET    /api/accounts/users/{id}/permissions/            # Ver permisos
GET    /api/accounts/users/search/?q=juan&institution_id=1  # Buscar
```

## Tests

Ejecuta los tests con:

```bash
python manage.py test apps.accounts.tests.test_models
python manage.py test apps.accounts.tests.test_services
python manage.py test apps.accounts.tests.test_api
```

### test_models.py

Tests unitarios de los modelos. Prueban validaciones y métodos sin HTTP.

### test_services.py

Tests de lógica de negocio con mocks. Verifican que los services lanzan excepciones apropiadas.

### test_api.py

Tests de integración HTTP. Prueban endpoints completos con APIClient.

## Ejemplos de Uso

### Crear un usuario en el código

```python
from apps.accounts.services.user_service import UserService

service = UserService()
user = service.create_user(
    dni='12345678',
    names='Juan',
    last_names='Pérez García',
    email='juan.perez@ejemplo.com',
    password='miContraseña123!',
    role_id=2,  # ID del rol
    institution_id=1
)

print(f"Usuario creado: {user.email}")
```

### Otorgar un permiso a un usuario

```python
from apps.accounts.services.user_service import UserService

service = UserService()
service.grant_permission(
    user_id=1,
    permission_codename='grading.create_note',
    reason='Permiso temporal para auditoría'
)
```

### Listar usuarios de un rol específico

```python
from apps.accounts.services.user_service import UserService

service = UserService()
docentes = service.list_users_by_role(role_id=2, institution_id=1)
for docente in docentes:
    print(f"{docente.names} {docente.last_names}: {docente.email}")
```

### Crear múltiples permisos

```python
from apps.accounts.services.permission_service import PermissionService

service = PermissionService()
permisos = [
    {'codename': 'grading.create_note', 'description': 'Crear notas', 'module': 'grading'},
    {'codename': 'grading.edit_note', 'description': 'Editar notas', 'module': 'grading'},
    {'codename': 'grading.delete_note', 'description': 'Eliminar notas', 'module': 'grading'},
]
service.create_permissions_bulk(permisos)
```

### Usar utilidades JWT

```python
from apps.accounts.utils import generate_access_token, decode_token

# Generar token
payload = {'user_id': 1}
token = generate_access_token(payload)

# Decodificar token
payload = decode_token(token)
print(f"User ID: {payload['user_id']}")
```

### Usar middleware y decoradores

```python
# En settings.py
MIDDLEWARE = [
    # ...
    'apps.accounts.middleware.JWTAuthMiddleware',
]

# En una vista
from rest_framework.decorators import api_view
from apps.accounts.decorators import require_permission

@api_view(['POST'])
@require_permission('grading.create_note')
def create_note(request):
    # Usuario garantizado que tiene el permiso
    return Response({'message': 'Nota creada'})
```

## Notas Importantes

1. **Password Hashing**: Usa `user.set_password()`, Django se encarga del resto.
2. **Soft Deletes**: Los usuarios se marcan como `active=False` en lugar de eliminarse.
3. **Auditoría**: `UserPermission` registra quién hizo cada cambio de permiso.
4. **Transacciones**: Los services usan transacciones atómicas cuando es necesario.
5. **Permisos Expiración**: `UserPermission.expires_at` permite permisos temporales.

## Integración con Otras Apps

Para verificar permisos en otra app:

```python
from apps.accounts.services.user_service import UserService

# En una vista o servicio
service = UserService()
if service.has_permission(user_id, 'grading.create_note'):
    # Permitir operación
    pass
else:
    # Denegar
    raise PermissionDenied()
```

## Migraciones

Cuando modificas modelos:

```bash
python manage.py makemigrations accounts
python manage.py migrate
```

Las migraciones se guardan en `apps/accounts/migrations/` (se crearán automáticamente).
