FROM python:3.9-slim

WORKDIR /app

# Instala dependencias primero (capa cacheable)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia solo lo necesario (respetando .dockerignore)
COPY . .

EXPOSE 5000
CMD ["python", "run.py"]