# Imagen base oficial de Python slim (ligera)
FROM python:3.11-slim

# Evita que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Evita buffering en logs (ves los prints en tiempo real)
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias del sistema necesarias para psycopg2 y otras libs
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependencias de Python primero
# (esto aprovecha el cache de Docker si requirements.txt no cambia)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto
COPY . .

# Asegurar que el script de entrada es ejecutable
RUN chmod +x /app/scripts/entrypoint.sh

# Crea directorio para archivos estáticos (opcional pero recomendado)
RUN mkdir -p /app/staticfiles

# Puerto que expone el contenedor
EXPOSE 8000

# ENTRYPOINT ejecuta el script que prepara la BD y luego el servidor
ENTRYPOINT ["/bin/bash", "/app/scripts/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]