# microservicio-notificaciones/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copia el archivo de requisitos e instala las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el archivo principal del microservicio
COPY main.py .

# Comando para iniciar la aplicación. El flag -u es crucial para ver los logs en tiempo real.
CMD ["python", "-u", "main.py"]