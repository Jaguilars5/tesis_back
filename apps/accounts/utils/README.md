# Utils — Utilidades de Identidad

Funciones auxiliares centralizadas para la gestión de tokens y el cálculo de permisos efectivos.

## Contenido Principal

### 1. JWT Helpers
Funciones para la gestión de ciclo de vida de tokens.
- `generate_access_token(payload)`: Crea un token de acceso (expiración corta).
- `generate_refresh_token(payload)`: Crea un token de refresco (expiración larga).
- `decode_token(token)`: Valida la firma y expiración de un JWT. Retorna el payload o `None`.

### 2. Permission Helpers
Lógica central de seguridad para el cálculo de accesos.
- `get_user_effective_permissions(user)`: Retorna un `set` con todos los codenames que el usuario tiene derecho a ejecutar.

#### Lógica de Cálculo:
1.  Obtiene todos los permisos vinculados al **Rol** del usuario.
2.  Aplica **Overrides** (UserPermission):
    -   Añade los marcados como `granted=True`.
    -   Remueve los marcados como `granted=False`.

## Ejemplo de Uso

```python
from apps.accounts.utils import generate_access_token, get_user_effective_permissions

# Generar token para un usuario
token = generate_access_token({'user_id': user.id})

# Consultar permisos reales (útil para auditoría)
perms = get_user_effective_permissions(user)
if 'grading.create_note' in perms:
    print("Acceso concedido")
```

> [!NOTE]
> Para la gestión de contraseñas, utilice siempre los métodos nativos del modelo: `user.set_password()` y `user.check_password()`.
