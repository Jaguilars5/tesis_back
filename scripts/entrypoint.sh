#!/bin/bash
set -e

# ═══════════════════════════════════════════════════════════════════════════
# ENTRYPOINT PARA DJANGO EN DOCKER
# Lee variables de .env y, opcionalmente, espera a la base de datos y ejecuta migraciones
# ═══════════════════════════════════════════════════════════════════════════

echo "🚀 Iniciando contenedor..."

# Valores por defecto: no bloquear servicios que no necesitan DB al arrancar
WAIT_FOR_DB=${WAIT_FOR_DB:-false}
RUN_MIGRATIONS=${RUN_MIGRATIONS:-false}

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
fi

# Crear datos iniciales si lo necesitas (opcional)
# python manage.py loaddata initial_data

if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "✨ Migraciones completadas"
fi
echo ""
echo "🌐 Iniciando proceso principal..."
echo "📊 Admin disponible en: http://localhost:8000/admin"
echo ""

# Ejecutar el servidor
exec "$@"
