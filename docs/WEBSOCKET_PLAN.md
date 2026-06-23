# Plan de implementación: WebSocket con Socket.IO

## Stack

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| Backend Server | `python-socketio` + `ASGIApp` | Servidor Socket.IO montado junto a Django |
| Backend Worker | `python-socketio` + `AsyncRedisManager` | Celery emite eventos vía Redis |
| Frontend | `socket.io-client` | Cliente con reconexión automática |
| Transporte | `redis://redis:6379/0` | Redis existente como backbone entre procesos |

## Arquitectura

```
Frontend (socket.io-client)
    │  ws://localhost:8000/ws/
    ▼
runserver (ASGI mode)
    │  ASGIApp de socket.io (intercepta /ws/, delega HTTP a Django)
    ▼
python-socketio.AsyncServer
    │  AsyncRedisManager
    ▼
Redis (channel layer)
    ▲
    │
Celery worker (proceso distinto)
    │  AsyncRedisManager.emit()
    ▼
python-socketio.AsyncServer → Frontend
```

## Rooms

Basado en `user_id`:

```python
# Backend — al conectar:
sio.enter_room(sid, f"user_{user.id}")

# Celery — al completar tarea:
sio.emit("task_completed", data, room=f"user_{user_id}")

# Preparado para futuros eventos:
# sio.emit("new_alert", data, room=f"user_{user_id}")
# sio.emit("grade_changed", data, room=f"user_{user_id}")
```

Cada usuario recibe solo sus propios eventos. Para broadcasts (ej. director viendo toda la institución), el usuario se une a rooms adicionales como `role_director` o `period_{id}`.

## Estructura de componentes

```
src/shared/
  contexts/
    SocketContext.tsx       ← Provider + context (expone socket sin lógica de reconexión)
  hooks/
    useSocket.ts            ← Crea y gestiona la conexión (reconexión, lifecycle)
    useSocketContext.ts     ← Hook que consume el context (alias)
  types/
    socket.events.ts        ← Tipos de eventos Socket.IO
```

## Flujo de conexión

```
1. App.tsx monta <SocketProvider>
2. SocketProvider llama a useSocket() internamente
3. useSocket() crea io(...) con:
   - auth: { token } del tokenManager
   - transports: ["websocket"]
4. Al conectar, envía autenticación automáticamente (socket.io lo hace en el handshake vía auth)
5. Tras autenticar, se une al room user_{id}
6. Cualquier componente hace useSocketContext() y socket.on("event", handler)
7. Cleanup: al desmontar, desconecta
```

---

## Fase 1 — Backend: Servidor Socket.IO

### Archivos a crear

| Archivo | Contenido |
|---------|-----------|
| `back/apps/analytics/socketio.py` | `AsyncServer` con `AsyncRedisManager`, eventos `connect`/`disconnect`, verificación JWT |
| `back/config/asgi.py` | `ASGIApp` de socket.io con Django como `other_app` |

### Archivos a modificar

| Archivo | Cambio |
|---------|--------|
| `back/requirements.txt` | + `python-socketio>=5.0` |
| `back/config/settings/base.py` | + `SOCKETIO_REDIS_URL`, + `ASGI_APPLICATION` |

### Detalle

**socketio.py:**
```python
import socketio
from socketio import ASGIApp
from socketio import AsyncRedisManager

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    client_manager=AsyncRedisManager("redis://redis:6379/0"),
)

@sio.event
async def connect(sid, environ, auth):
    token = auth.get("token") if auth else None
    if not token:
        return False

    user = await verify_token(token)
    if not user:
        return False

    await sio.save_session(sid, {"user_id": user.id, "user": user})
    await sio.enter_room(sid, f"user_{user.id}")
    return True

@sio.event
async def disconnect(sid):
    session = await sio.get_session(sid)
    user_id = session.get("user_id")
    if user_id:
        await sio.leave_room(sid, f"user_{user_id}")
```

**asgi.py:**
```python
from socketio import ASGIApp
from django.core.asgi import get_asgi_application
from apps.analytics.socketio import sio

django_asgi = get_asgi_application()
application = ASGIApp(sio, other_app=django_asgi)
```

### Criterio de éxito
- `runserver` inicia sin errores
- Cliente Socket.IO puede conectarse a `ws://localhost:8000`
- Conexión rechazada si el token JWT es inválido

---

## Fase 2 — Backend: Emisión desde Celery

### Archivos a modificar

| Archivo | Cambio |
|---------|--------|
| `back/apps/analytics/tasks.py` | `batch_calculate_academic_risk` emite `task_completed` al room del usuario |

### Detalle

```python
from django.conf import settings
from socketio import AsyncRedisManager

@shared_task(bind=True)
def batch_calculate_academic_risk(self, academic_period_id, student_ids, user_id=None):
    # ... lógica existente ...
    results = {"total": total, "processed": processed, "failed": failed}

    if user_id:
        try:
            sio_manager = AsyncRedisManager(settings.SOCKETIO_REDIS_URL)
            from asgiref.sync import async_to_sync
            async_to_sync(sio_manager.emit)(
                "task_completed",
                {"task_id": self.request.id, "result": results},
                room=f"user_{user_id}",
            )
        except Exception:
            logger.warning("No se pudo emitir evento Socket.IO", exc_info=True)

    return results
```

**Nota:** `recalculate_period` en `views.py` debe pasar `request.user.id` a la tarea:
```python
task = batch_calculate_academic_risk.delay(period_id, student_ids, user_id=request.user.id)
```

### Criterio de éxito
- Al completar `batch_calculate_academic_risk`, se emite evento a Redis
- Cliente Socket.IO conectado recibe el evento

---

## Fase 3 — Frontend: Contexto Socket.IO

### Archivos a crear

| Archivo | Contenido |
|---------|-----------|
| `web-front/src/shared/types/socket.events.ts` | Interfaces tipadas de eventos |
| `web-front/src/shared/hooks/useSocket.ts` | Hook que crea/administra la conexión |
| `web-front/src/shared/contexts/SocketContext.tsx` | Provider + Context + `useSocketContext` |

### Archivos a modificar

| Archivo | Cambio |
|---------|--------|
| `web-front/package.json` | + `socket.io-client` |
| `web-front/src/App.tsx` | Envolver con `<SocketProvider>` |

### Detalle

**socket.events.ts:**
```typescript
export interface TaskCompletedEvent {
  task_id: string;
  result: {
    total: number;
    processed: number;
    failed: number;
  };
}

export interface SocketEventMap {
  task_completed: TaskCompletedEvent;
}

export type SocketEventName = keyof SocketEventMap;

export type SocketEventData<T extends SocketEventName> =
  T extends keyof SocketEventMap ? SocketEventMap[T] : never;
```

**useSocket.ts:**
```typescript
export function useSocket(token: string | null) {
  const socketRef = useRef<Socket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!token) return;

    const socket = io({
      auth: { token },
      transports: ["websocket"],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 2000,
    });

    socket.on("connect", () => setConnected(true));
    socket.on("disconnect", () => setConnected(false));
    socket.on("connect_error", () => setConnected(false));

    socketRef.current = socket;

    return () => {
      socket.disconnect();
      socketRef.current = null;
      setConnected(false);
    };
  }, [token]);

  return { socket: socketRef.current, connected };
}
```

**SocketContext.tsx:**
```typescript
interface SocketContextValue {
  socket: Socket | null;
  connected: boolean;
}

const SocketContext = createContext<SocketContextValue>({
  socket: null,
  connected: false,
});

export function SocketProvider({ children }: { children: ReactNode }) {
  const token = useAppSelector(selectAccessToken);
  const { socket, connected } = useSocket(token);

  return (
    <SocketContext.Provider value={{ socket, connected }}>
      {children}
    </SocketContext.Provider>
  );
}

export const useSocketContext = () => useContext(SocketContext);
```

### Criterio de éxito
- App renderiza sin errores
- `useSocketContext()` devuelve socket no-null cuando hay token
- `connected` es `true` cuando el WebSocket está activo

---

## Fase 4 — Frontend: Integración en RiskScoreListPage

### Archivos a modificar

| Archivo | Cambio |
|---------|--------|
| `web-front/src/features/analytics/presentation/pages/RiskScoreListPage.tsx` | Eliminar polling, escuchar `task_completed` vía `useSocketContext` |
| `web-front/src/features/analytics/presentation/reducers/riskScore.thunks.ts` | Eliminar `checkTaskStatus` |
| `web-front/src/features/analytics/presentation/reducers/riskScore.reducer.ts` | Eliminar handlers de `checkTaskStatus` |
| `web-front/src/features/analytics/presentation/hooks/useRiskScoreController.ts` | Eliminar `checkStatus` |

### Detalle

```typescript
// RiskScoreListPage.tsx
const { socket } = useSocketContext();

useEffect(() => {
  if (!socket || !calcTaskId) return;

  const handler = (data: TaskCompletedEvent) => {
    if (data.task_id === calcTaskId) {
      toast("Cálculo completado", "success");
      resetCalc();
      if (effectivePeriodId) {
        loadScores({ academic_period: effectivePeriodId, page: 1, pageSize: 10 });
      }
    }
  };

  socket.on("task_completed", handler);
  return () => { socket.off("task_completed", handler); };
}, [socket, calcTaskId, effectivePeriodId, loadScores, resetCalc]);
```

### Criterio de éxito
- Al hacer recalcular, aparece "Cálculo en segundo plano..."
- Cuando Celery termina, desaparece el banner y se recarga la lista
- Sin errores TypeScript

---

## Fase 5 — Limpieza

### Archivos a modificar

| Archivo | Cambio |
|---------|--------|
| `back/apps/analytics/api/views.py` | Eliminar endpoint `task_status` y su permiso |
| `back/apps/analytics/api/views.py` | Pasar `request.user.id` a `batch_calculate_academic_risk.delay()` |
| `web-front/src/features/analytics/domain/constants/analytics.constants.ts` | Eliminar `CHECK_TASK_STATUS`, `TASK_STATUS` |
| `web-front/src/features/analytics/domain/repositories/analytics.repository.ts` | Eliminar `CheckTaskStatusParamsT`, `checkTaskStatus` |
| `web-front/src/features/analytics/infrastructure/repositories/analytics-api.repository.ts` | Eliminar `checkTaskStatus` |
| `web-front/src/features/analytics/domain/entities/analytics.types.ts` | Eliminar `TaskStatusT` (si ya no se usa) |

### Criterio de éxito
- `git diff` muestra solo los cambios necesarios
- 0 errores TypeScript

---

## Resumen de archivos

### Crear (7)

| # | Archivo | Fase |
|---|---------|------|
| 1 | `back/apps/analytics/socketio.py` | 1 |
| 2 | `back/config/asgi.py` | 1 |
| 3 | `web-front/src/shared/types/socket.events.ts` | 3 |
| 4 | `web-front/src/shared/hooks/useSocket.ts` | 3 |
| 5 | `web-front/src/shared/contexts/SocketContext.tsx` | 3 |

### Modificar (12)

| # | Archivo | Fase |
|---|---------|------|
| 1 | `back/requirements.txt` | 1 |
| 2 | `back/config/settings/base.py` | 1 |
| 3 | `back/apps/analytics/tasks.py` | 2 |
| 4 | `web-front/package.json` | 3 |
| 5 | `web-front/src/App.tsx` | 3 |
| 6 | `back/apps/analytics/api/views.py` | 5 |
| 7 | `web-front/src/features/analytics/presentation/pages/RiskScoreListPage.tsx` | 4 |
| 8 | `web-front/src/features/analytics/presentation/reducers/riskScore.thunks.ts` | 4 |
| 9 | `web-front/src/features/analytics/presentation/reducers/riskScore.reducer.ts` | 4 |
| 10 | `web-front/src/features/analytics/presentation/hooks/useRiskScoreController.ts` | 4 |
| 11 | `web-front/src/features/analytics/domain/constants/analytics.constants.ts` | 5 |
| 12 | `web-front/src/features/analytics/domain/repositories/analytics.repository.ts` | 5 |
