# Utils — Utilidades

Funciones auxiliares reutilizables para el módulo accounts.

## Contenido

### JWT Helpers

- `generate_access_token(payload)` — Crea un JWT access token
- `generate_refresh_token(payload)` — Crea un JWT refresh token
- `decode_token(token)` — Decodifica y valida un JWT

### Password Helpers

- `hash_password(plain)` — Genera hash bcrypt
- `verify_password(plain, hashed)` — Verifica contraseña

### Permission Helpers

- `get_user_effective_permissions(user)` — Calcula permisos efectivos (role + overrides)

## Uso

```python
from apps.accounts.utils import hash_password, decode_token

hashed = hash_password('micontraseña123')
payload = decode_token(jwt_token)
```
