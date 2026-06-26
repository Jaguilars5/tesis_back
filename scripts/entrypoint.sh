#!/bin/bash
set -e

# ═══════════════════════════════════════════════════════════════════════════
# ENTRYPOINT PARA DJANGO EN DOCKER
# Lee variables de .env y, opcionalmente, espera a la base de datos y ejecuta migraciones
# ═══════════════════════════════════════════════════════════════════════════

echo "🚀 Iniciando contenedor..."

# Valores por defecto.
# RUN_MIGRATIONS=true por defecto: el contenedor SIEMPRE aplica migraciones (migrate),
# nunca genera migraciones (makemigrations) en tiempo de ejecución.
# Los servicios que no usan DB (celery/flower) lo desactivan vía docker-compose.
WAIT_FOR_DB=${WAIT_FOR_DB:-false}
RUN_MIGRATIONS=${RUN_MIGRATIONS:-true}
RUN_SEED=${RUN_SEED:-false}

if [ "$WAIT_FOR_DB" = "true" ]; then
  echo "⏳ Esperando a PostgreSQL..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 0.1
  done
  echo "✅ PostgreSQL está listo"
fi

if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "🔄 Ejecutando migraciones..."
  python manage.py migrate --noinput
  echo "📦 Recolectando archivos estáticos..."
  python manage.py collectstatic --noinput
  echo "✨ Migraciones completadas"
fi

# Seeds idempotentes (opcional, controlado por RUN_SEED).
# Solo deberían ejecutarse en un servicio (web) para evitar duplicación de trabajo.
if [ "$RUN_SEED" = "true" ]; then
  echo "🌱 Ejecutando seeds..."
  python manage.py seed_catalogs
  python manage.py seed_permissions
  python manage.py seed_test_data
  echo "🌱 Seeds completados"
fi
echo ""
echo "🌐 Iniciando proceso principal..."
echo "📊 Admin disponible en: http://localhost:8000/admin"
echo ""

# Ejecutar el servidor
exec "$@"
