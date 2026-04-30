# Middleware de Seguridad

El módulo `accounts` proporciona una capa de interceptación global para gestionar la identidad del usuario en cada petición HTTP.

## Componente: `JWTAuthMiddleware`

Este middleware analiza el header `Authorization` buscando un token de tipo **Bearer**. Si el token es válido, enriquece el objeto `request` con datos de identidad y autorizaciones.

### Atributos Inyectados
Al usar este middleware, los siguientes atributos estarán disponibles en todas las vistas:

- `request.current_user`: Instancia del modelo `User`. Será `None` si el token es inválido, expiró o no se proporcionó.
- `request.user_permissions`: Un `set` de strings con los codenames de permisos efectivos (ej: `{'grading.view_note', 'academic.edit_mesh'}`). Incluye permisos del rol + excepciones individuales.
- `request.token_payload`: El contenido decodificado del JWT (útil para verificar tipos de token, fechas de emisión o `user_id`).

## Procesamiento de Rutas

El middleware divide el tráfico del sistema en dos categorías principales:

### 1. Rutas Públicas (Exentas)
Configuradas en `PUBLIC_PATHS`. No requieren token y son accesibles de forma anónima. El middleware no intenta decodificar nada.
- `/api/accounts/login/`: Autenticación inicial.
- `/api/accounts/refresh/`: Renovación de tokens de acceso.

### 2. Rutas Protegidas (Por Defecto)
Cualquier otra ruta que empiece por `/api/`. El middleware intenta extraer y validar el token.
- **Token Válido**: Llena los atributos del `request` y permite que la petición continúe.
- **Sin Token / Token Inválido**: Los atributos quedan vacíos (`None`). La petición continúa, pero las vistas protegidas por decoradores o permisos de DRF lanzarán errores `401` o `403`.

## Configuración e Instalación

Asegúrese de registrar el middleware en su archivo `settings.py`:

```python
MIDDLEWARE = [
    # ... otros middleware ...
    'apps.accounts.middleware.JWTAuthMiddleware',
]
```

## Ejemplo de Uso (Header HTTP)

Para que el middleware procese la identidad, el cliente debe enviar el token en cada petición:

**Request Header:**
```http
Authorization: Bearer <tu_access_token_aqui>
```

**Ejemplo con cURL:**
```bash
curl -H "Authorization: Bearer eyJhbG..." http://localhost:8000/api/accounts/users/
```

## Ejemplo de Uso en Lógica de Vistas

```python
def mi_vista(request):
    # Verificación manual de autenticación
    if not request.current_user:
        return Response({"ok": False, "msg": "No autenticado"}, status=401)
    
    # Verificación manual de permisos
    if 'grading.create_note' in request.user_permissions:
        return Response({"ok": True, "msg": "Acceso permitido"})
```
