#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
# VERIFICADOR DE CONFIGURACIÓN DOCKER
# Chequea que todo esté configurado correctamente antes de iniciar
# ═══════════════════════════════════════════════════════════════════════════

echo "═══════════════════════════════════════════════════════════════════════════"
echo "🔍 VERIFICADOR DE CONFIGURACIÓN DOCKER"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Contador de problemas
ISSUES=0

# 1. Verificar Docker
echo "1️⃣  Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker no está instalado${NC}"
    ISSUES=$((ISSUES+1))
else
    echo -e "${GREEN}✓ Docker instalado${NC}"
fi

# 2. Verificar Docker Compose
echo ""
echo "2️⃣  Verificando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose no está instalado${NC}"
    ISSUES=$((ISSUES+1))
else
    echo -e "${GREEN}✓ Docker Compose instalado${NC}"
fi

# 3. Verificar archivos necesarios
echo ""
echo "3️⃣  Verificando archivos de configuración..."

FILES=(
    "Dockerfile"
    "docker-compose.yml"
    ".env"
    "requirements.txt"
    "scripts/entrypoint.sh"
    "manage.py"
    "config/settings/local.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}✗ $file NO ENCONTRADO${NC}"
        ISSUES=$((ISSUES+1))
    fi
done

# 4. Verificar variables .env
echo ""
echo "4️⃣  Verificando variables de ambiente en .env..."

REQUIRED_VARS=(
    "DEBUG"
    "SECRET_KEY"
    "DB_NAME"
    "DB_USER"
    "DB_PASSWORD"
    "DB_HOST"
    "DB_PORT"
    "REDIS_URL"
    "CELERY_BROKER_URL"
)

for var in "${REQUIRED_VARS[@]}"; do
    if grep -q "^$var=" .env; then
        VALUE=$(grep "^$var=" .env | cut -d'=' -f2)
        echo -e "${GREEN}✓ $var = ${VALUE:0:30}...${NC}"
    else
        echo -e "${YELLOW}⚠ $var NO definido en .env${NC}"
    fi
done

# 5. Verificar requirements.txt
echo ""
echo "5️⃣  Verificando dependencias críticas en requirements.txt..."

PACKAGES=(
    "Django"
    "djangorestframework"
    "psycopg2-binary"
    "celery"
    "redis"
    "gunicorn"
    "python-dotenv"
)

for pkg in "${PACKAGES[@]}"; do
    if grep -qi "$pkg" requirements.txt; then
        echo -e "${GREEN}✓ $pkg${NC}"
    else
        echo -e "${RED}✗ $pkg FALTA${NC}"
        ISSUES=$((ISSUES+1))
    fi
done

# 6. Verificar Dockerfile
echo ""
echo "6️⃣  Verificando Dockerfile..."

DOCKERFILE_CHECKS=(
    "python:3.11"
    "psycopg2"
    "netcat-openbsd"
    "EXPOSE 8000"
    "entrypoint.sh"
)

for check in "${DOCKERFILE_CHECKS[@]}"; do
    if grep -q "$check" Dockerfile; then
        echo -e "${GREEN}✓ $check${NC}"
    else
        echo -e "${YELLOW}⚠ $check NO encontrado en Dockerfile${NC}"
    fi
done

# 7. Verificar docker-compose.yml
echo ""
echo "7️⃣  Verificando docker-compose.yml..."

COMPOSE_CHECKS=(
    "postgres:15"
    "redis:7"
    "web:"
    "celery:"
    "depends_on:"
)

for check in "${COMPOSE_CHECKS[@]}"; do
    if grep -q "$check" docker-compose.yml; then
        echo -e "${GREEN}✓ $check${NC}"
    else
        echo -e "${RED}✗ $check NO encontrado${NC}"
        ISSUES=$((ISSUES+1))
    fi
done

# Resumen
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ TODO ESTÁ CONFIGURADO CORRECTAMENTE${NC}"
    echo ""
    echo "Próximos pasos:"
    echo "  1. docker-compose build"
    echo "  2. docker-compose up"
    echo ""
    echo "Luego en otra terminal:"
    echo "  docker-compose exec web python manage.py createsuperuser"
else
    echo -e "${RED}⚠️  SE ENCONTRARON $ISSUES PROBLEMA(S)${NC}"
    echo ""
    echo "Por favor corrige los problemas listados arriba."
fi
echo "═══════════════════════════════════════════════════════════════════════════"
