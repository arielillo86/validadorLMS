# Usar imagen base de Ubuntu
FROM ubuntu:20.04

# Configurar entorno sin interacción
ENV DEBIAN_FRONTEND=noninteractive

# 1. Instalar todas las dependencias necesarias en un solo RUN
RUN apt-get update && \
    apt-get install -y \
    python3.9 \
    python3-pip \
    python3.9-venv \
    python3.9-dev \
    gcc && \
    # Limpieza en el mismo RUN para reducir tamaño de imagen
    apt-get clean && \
    rm -rf \
    /var/lib/apt/lists/* \
    /var/cache/apt/archives \
    /tmp/* \
    /var/tmp/* \
    /usr/share/man \
    /usr/share/doc

# 2. Configurar enlaces simbólicos
RUN ln -sf /usr/bin/python3.9 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# 3. Crear y configurar entorno virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 4. Configurar directorio de trabajo
WORKDIR /app

# 5. Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar aplicación
COPY . .

# 7. Configurar persistencia
RUN mkdir -p /data/uploads && \
    chmod -R 777 /data

# 8. Variables de entorno
ENV FLASK_APP=run.py \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    SQLITE_DB_FILE=/data/database.db \
    UPLOAD_FOLDER=/data/uploads

# 9. Configurar usuario no-root
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser appuser && \
    chown -R appuser:appuser /app /data

USER appuser

EXPOSE 5000

CMD ["gunicorn", \
    "--bind", "0.0.0.0:5000", \
    "--workers", "1", \
    "--threads", "4", \
    "--worker-class", "gthread", \
    "--timeout", "120", \
    "run:app"]