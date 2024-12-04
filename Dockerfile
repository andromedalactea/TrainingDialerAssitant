# Usa una imagen base de Python 3.10 slim
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para WeasyPrint y otras herramientas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libgirepository1.0-dev \
    libxml2 \
    libxslt1-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia solo las dependencias necesarias (requirements.txt)
COPY requirements.txt .

# Instala las dependencias de Python en el contenedor
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos los archivos de la aplicación en el contenedor
COPY . .

# Exponer el puerto 8080 para la aplicación FastAPI
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["python", "scripts/app_fast_api.py"]