# Backend Dockerfile para Escudo Escolar
FROM python:3.11-slim

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv (gestor de paquetes rápido)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copiar archivos de dependencias
COPY pyproject.toml README.md ./

# Instalar dependencias con uv
RUN uv sync

# Copiar el código de la aplicación
COPY . .

# Crear directorio para el modelo (si no existe)
RUN mkdir -p /app/models

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
