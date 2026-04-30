# Middleware

Middleware personalizado para el módulo accounts.

## Contenido

### JWTAuthMiddleware

Procesa tokens JWT en cada request y inyecta:

- `request.current_user` — Instancia del User autenticado (o None)
- `request.user_permissions` — Set de codenames de permisos efectivos
- `request.token_payload` — Payload del JWT decodificado

**Comportamiento:**

- Rutas públicas (login, refresh) no requieren token
- Rutas protegidas verifican presencia y validez del token
- Vistas pueden usar `@require_permission()` para protegerse

## Uso

```python
# En settings.py
MIDDLEWARE = [
    # ... otros middleware ...
    'apps.accounts.middleware.JWTAuthMiddleware',
]

# En una vista
def my_view(request):
    if request.current_user:
        print(f"Usuario: {request.current_user.email}")
        print(f"Permisos: {request.user_permissions}")
```
