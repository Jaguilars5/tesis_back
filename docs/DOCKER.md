# Docker y Containerización

Este documento describe la configuración de Docker para ejecutar el sistema de gestión académica en contenedores aislados, facilitando el desarrollo y la consistencia entre ambientes.

## Visión General

El proyecto está configurado para ejecutarse completamente en Docker con los siguientes servicios:

- **PostgreSQL 15**: Base de datos principal (puerto 5432)
- **Redis 7**: Cache y broker para Celery (puerto 6379)
- **Django**: Aplicación web (puerto 8000)
- **Celery**: Procesador de tareas asincrónicas
- **Flower**: Monitor visual de Celery (puerto 5555)

## Requisitos Previos

```bash
# Instalaciones necesarias
- Docker >= 20.10
- Docker Compose >= 2.0
```

Verifica tu instalación:

```bash
docker --version
docker-compose --version
```

## Estructura de Archivos Docker

```text
proyecto/
├── Dockerfile                    # Especificación de imagen
├── docker-compose.yml            # Orquestación de servicios
├── entrypoint.sh                 # Script de inicialización (movido a scripts/)
├── .env                          # Variables de entorno (desarrollo)
├── .env.example                  # Plantilla de variables
├── scripts/
│   ├── entrypoint.sh            # Preparación de contenedor
│   └── verify_docker_setup.sh   # Verificador de configuración
└── docs/DOCKER.md               # Este archivo
```

## Configuración de Servicios

### Base de Datos (PostgreSQL)

```yaml
db:
  image: postgres:15-alpine
  container_name: tesis_db
  environment:
    POSTGRES_DB: ${DB_NAME}
    POSTGRES_USER: ${DB_USER}
    POSTGRES_PASSWORD: ${DB_PASSWORD}
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"
```

**Características:**

- Imagen ligera (alpine)
- Datos persistentes en volumen `postgres_data`
- Health checks para sincronización entre servicios

### Redis

```yaml
redis:
  image: redis:7-alpine
  container_name: tesis_redis
  ports:
    - "6379:6379"
```

**Usos:**

- Cache de sesiones y datos
- Broker para colas de Celery
- Almacenamiento de resultados de tareas

### Aplicación Django (web)

```yaml
web:
  build: .
  container_name: tesis_web
  command: python manage.py runserver 0.0.0.0:8000
  volumes:
    - .:/app
  ports:
    - "8000:8000"
  depends_on:
    db:
      condition: service_healthy
    redis:
      condition: service_healthy
```

**Características:**

- Código en volumen para cambios en vivo
- Dependencias con health checks
- Puerto 8000 accesible desde localhost

### Celery Worker

```yaml
celery:
  build: .
  container_name: tesis_celery
  command: celery -A config worker --loglevel=info
  depends_on:
    db:
      condition: service_healthy
    redis:
      condition: service_healthy
```

**Responsabilidades:**

- Procesamiento de tareas asincrónicas
- Se conecta a Redis como broker
- Persiste resultados en PostgreSQL

### Flower (Monitor opcional)

```yaml
flower:
  build: .
  container_name: tesis_flower
  command: celery -A config flower --port=5555
  ports:
    - "5555:5555"
```

Accede en http://localhost:5555 para monitorear tareas en tiempo real.

## Variables de Entorno

### Desarrollo (.env)

```env
# ─── DJANGO ──────────────────────────────────────────────────────────────────
DEBUG=True
SECRET_KEY=django-insecure-dev-key-change-in-production-12345
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,web

# ─── BASE DE DATOS (PostgreSQL) ──────────────────────────────────────────────
DB_NAME=tesis_db
DB_USER=tesis_user
DB_PASSWORD=tesis_password
DB_HOST=db                  # ⚠️ Nombre del servicio en Docker, NO localhost
DB_PORT=5432

# ─── REDIS / CELERY ──────────────────────────────────────────────────────────
REDIS_URL=redis://redis:6379/1      # ⚠️ redis es el nombre del servicio
CELERY_BROKER_URL=redis://redis:6379/0

# ─── EMAIL ───────────────────────────────────────────────────────────────────
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=Sistema Académico <dev@localhost>

# ─── CORS ────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000
```

### Producción (no incluido en repo)

```env
DEBUG=False
SECRET_KEY=<generar-clave-segura-aleatoria>
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
DB_HOST=<host-produccion>
DB_PASSWORD=<contraseña-super-segura>
REDIS_URL=redis://<host-produccion>:6379/0
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=<tu-email>
EMAIL_HOST_PASSWORD=<app-password>
```

**⚠️ Importante:** Nunca hagas commit de variables sensibles. Usa `.env.example` como plantilla.

## Ciclo de Vida del Desarrollo

### Instalación Inicial

```bash
# 1. Clonar el repositorio
git clone https://github.com/Jaguilars5/tesis_back.git
cd tesis_back

# 2. Crear archivo .env desde plantilla (si no existe)
cp .env.example .env

# 3. Construir imagen Docker
docker-compose build

# 4. Iniciar servicios
docker-compose up

# 5. En otra terminal: crear superuser
docker-compose exec web python manage.py createsuperuser

# 6. Cargar datos iniciales (si existen)
docker-compose exec web python manage.py loaddata initial_data
```

### Desarrollo Diario

```bash
# Iniciar todos los servicios
docker-compose up

# Ver logs en tiempo real
docker-compose logs -f web

# Ejecutar comandos Django
docker-compose exec web python manage.py <comando>

# Acceder al shell de Django
docker-compose exec web python manage.py shell

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear un modelo nuevo
docker-compose exec web python manage.py makemigrations

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (⚠️ borra BD)
docker-compose down -v
```

### Testing

```bash
# Ejecutar todas las pruebas
docker-compose exec web python manage.py test

# Tests de una aplicación específica
docker-compose exec web python manage.py test apps.academic

# Con cobertura
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```

## Verificación de Configuración

Se incluye un script automatizado para verificar que todo está configurado correctamente:

```bash
bash scripts/verify_docker_setup.sh
```

Verifica:

- ✓ Docker instalado
- ✓ Archivos de configuración presentes
- ✓ Variables de entorno necesarias
- ✓ Dependencias en requirements.txt
- ✓ Configuración de Dockerfile y docker-compose.yml

Debería mostrar: **✅ TODO ESTÁ CONFIGURADO CORRECTAMENTE**

## Logs y Debugging

### Ver logs de un servicio

```bash
# Web (Django)
docker-compose logs -f web

# Base de datos
docker-compose logs -f db

# Redis
docker-compose logs -f redis

# Celery worker
docker-compose logs -f celery

# Flower (Celery monitor)
docker-compose logs -f flower

# Todos los servicios
docker-compose logs -f
```

### Ejecutar comandos interactivos

```bash
# Shell SQL en PostgreSQL
docker-compose exec db psql -U $DB_USER -d $DB_NAME

# CLI de Redis
docker-compose exec redis redis-cli

# Shell interactivo de Django
docker-compose exec web python manage.py shell

# Comandos personalizados
docker-compose exec web python <script.py>
```

## Problemas Comunes

### "ConnectionRefusedError: PostgreSQL"

**Síntoma:** El contenedor web no puede conectarse a la BD.

**Solución:**

```bash
# Verificar que PostgreSQL está running
docker-compose ps

# Ver logs
docker-compose logs db

# Reiniciar
docker-compose restart db

# Verificar variables .env
grep DB_HOST .env     # Debe ser 'db', no 'localhost'
grep DB_PORT .env     # Debe ser 5432
```

### "Cannot assign requested address: Redis"

**Síntoma:** Celery no puede conectarse a Redis.

**Solución:**

```bash
docker-compose restart redis
docker-compose logs redis

# Verificar variables
grep REDIS_URL .env    # Debe usar 'redis://', no 'localhost'
```

### Cambios en código no se reflejan

**Síntoma:** Modifiqué un archivo pero el cambio no aparece.

**Solución:**

```bash
# El código está en volumen, pero Django necesita recargarse
docker-compose restart web

# O reiniciar todo
docker-compose down
docker-compose up
```

### Puerto ya en uso

**Síntoma:** "bind: address already in use"

**Solución:**

```bash
# Identificar proceso usando el puerto
lsof -i :8000

# Matar proceso
kill -9 <PID>

# O cambiar puerto en docker-compose.yml
# Cambiar: "8000:8000" por "9000:8000"
```

### Migraciones no se ejecutan

**Síntoma:** Error "table does not exist"

**Solución:**

```bash
# Ejecutar manualmente
docker-compose exec web python manage.py migrate

# Verificar el estado de migraciones
docker-compose exec web python manage.py showmigrations

# Revertir una migración si es necesario
docker-compose exec web python manage.py migrate app_name 0001
```

## Limpieza y Mantenimiento

### Limpiar volúmenes y contenedores

```bash
# Detener todo y eliminar volúmenes (⚠️ borra datos)
docker-compose down -v

# Eliminar imágenes (para reconstruir desde cero)
docker rmi tesis_back-web tesis_back-celery tesis_back-flower

# Reconstruir desde cero
docker-compose build --no-cache
docker-compose up
```

### Monitoreo de recursos

```bash
# Ver uso de CPU/memoria
docker stats

# Ver contenedores activos
docker ps

# Ver todas las imágenes
docker images

# Ver volúmenes
docker volume ls
```

## Conexión Remota a Bases de Datos

### PostgreSQL desde tu máquina

```bash
# Conexión directa
psql -h localhost -U tesis_user -d tesis_db -p 5432

# Herramientas gráficas (DBeaver, pgAdmin, etc.)
Host:     localhost
Puerto:   5432
Usuario:  tesis_user
Contraseña: (ver .env)
BD:       tesis_db
```

### Redis desde tu máquina

```bash
# CLI interactiva
redis-cli -h localhost -p 6379

# Ver keys
KEYS *

# Monitorear conexiones
MONITOR
```

## Mejores Prácticas

### Desarrollo

1. **Nunca modifiques variables sensibles en .env**
   - Usa .env.example como referencia
   - Cada dev tiene su propio .env

2. **Commitea cambios en Dockerfile/docker-compose.yml**
   - Avisa al equipo de cambios en dependencias
   - Ejecuta `docker-compose build` después de cambios

3. **Usa volúmenes para código**
   - Cambios en vivo sin reconstruir
   - Debugging más rápido

4. **Limpiar regularmente**
   ```bash
   docker-compose down -v    # Semanal
   docker system prune        # Mensual
   ```

### Producción

1. **Nunca uses `runserver` en producción**
   - Usa Gunicorn: `gunicorn config.wsgi:application`
   - Configura Nginx como reverse proxy

2. **Variables sensibles en secrets/environment**
   - No en archivos dentro de la imagen
   - Usa orquestadores (Docker Swarm, Kubernetes)

3. **Monitoreo y logging**
   - Centraliza logs (ELK, Splunk, DataDog)
   - Alertas en uso de recursos
   - Backups automáticos de BD

4. **Seguridad**
   - Imagenes base actualizada
   - Escanea vulnerabilidades: `docker scan`
   - Network isolation entre servicios

## Referencias

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment with Docker](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [PostgreSQL en Docker](https://hub.docker.com/_/postgres)
- [Redis en Docker](https://hub.docker.com/_/redis)
- [Celery Configuration](https://docs.celeryproject.io/en/stable/django/)

## Contacto

Para problemas específicos del setup Docker, consulta:

1. Este documento (DOCKER.md)
2. Logs: `docker-compose logs -f`
3. Script verificador: `bash scripts/verify_docker_setup.sh`
