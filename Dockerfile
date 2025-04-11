# Usar imagen base de Ubuntu
FROM ubuntu:20.04

# Configurar entorno sin interacción
ENV DEBIAN_FRONTEND=noninteractive

# 1. Instalar dependencias como root
RUN apt-get update && \
    apt-get install -y \
    python3.9 \
    python3-pip \
    python3.9-venv \
    python3.9-dev \
    gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/man /usr/share/doc

# 2. Configurar Python
RUN ln -sf /usr/bin/python3.9 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip && \
    python -m venv /opt/venv

# 3. Directorios críticos con permisos globales
RUN mkdir -p /app/uploads /data/uploads && \
    chmod -R 777 /app/uploads /data/uploads

# 4. Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar aplicación
WORKDIR /app
COPY . .

# 6. Variables de entorno
ENV FLASK_APP=run.py \
    FLASK_ENV=production \
    UPLOAD_FOLDER=/app/uploads

# 7. Ejecutar como root (TEMPORAL - solo para desarrollo)
USER root

EXPOSE 5000

CMD ["gunicorn", \
    "--bind", "0.0.0.0:5000", \
    "--workers", "1", \
    "--threads", "4", \
    "--worker-class", "gthread", \
    "--timeout", "120", \
    "run:app"]