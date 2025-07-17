# microservicio-notificaciones/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar toda la estructura del microservicio
COPY main.py .
COPY consumer/ consumer/
COPY mailer/ mailer/
COPY config/ config/

# Comando de arranque
CMD ["python", "-u", "main.py"]
