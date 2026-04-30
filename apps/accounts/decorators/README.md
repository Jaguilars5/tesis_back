# Decoradores de Seguridad

Los decoradores permiten proteger de forma declarativa las vistas basadas en funciones.

## `@require_permission(codename)`

Este decorador verifica que el usuario autenticado posea el permiso especificado en sus permisos efectivos.

### Flujo de Validación
1.  **Verificación de Identidad**: Si `request.current_user` es `None`, retorna `401 Unauthorized`.
2.  **Verificación de Autorización**: Si el `codename` no está presente en `request.user_permissions`, retorna `403 Forbidden`.
3.  **Ejecución**: Si ambas pasan, se ejecuta la lógica de la vista.

### Formato de Error
En caso de falla, el decorador retorna una respuesta estandarizada:
```json
{
    "ok": false,
    "data": {},
    "msg": "Mensaje descriptivo del error"
}
```

## Ejemplo de Implementación

```python
from rest_framework.decorators import api_view
from apps.accounts.decorators import require_permission

@api_view(['POST'])
@require_permission('grading.create_note')
def guardar_nota(request):
    # Aquí ya sabemos que request.current_user existe 
    # y tiene el permiso 'grading.create_note'
    return Response({"ok": True, "msg": "Nota guardada"})
```

> [!TIP]
> Para clases `ViewSet`, se recomienda usar `permission_classes` de Django REST Framework en lugar de este decorador.
