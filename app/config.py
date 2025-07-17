import os

def configure_environment(app):
    app.config["REPORT_MICROSERVICE_URL"] = os.getenv("REPORT_MICROSERVICE_URL", "http://kong:8000/report/generate")
    app.config["REDIS_HOST"] = os.getenv("REDIS_HOST", "redis")
    app.config["REDIS_PORT"] = int(os.getenv("REDIS_PORT", 6379))
    app.config["REDIS_DB"] = int(os.getenv("REDIS_DB", 0))
