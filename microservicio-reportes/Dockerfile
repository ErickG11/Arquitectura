FROM python:3.10-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponer el puerto 80 (documentación)
EXPOSE 80

# Arrancar uvicorn en el puerto 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

