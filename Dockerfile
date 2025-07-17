# Dockerfile (monolito)

FROM python:3.10-bullseye

ENV ACCEPT_EULA=Y \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app  

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl gnupg2 ca-certificates unixodbc unixodbc-dev \
 && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
 && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update \
 && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
