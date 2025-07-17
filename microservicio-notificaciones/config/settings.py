import os

EMAIL_SENDER = os.getenv("EMAIL_SENDER", "grandaerick10@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "yfcg acxf ppwc dgjy")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", 587))
NOTIFICATION_RECIPIENT = os.getenv("NOTIFICATION_RECIPIENT", "grandaerick04@gmail.com")
MIN_RISK_LEVEL_FOR_NOTIFICATION = int(os.getenv("MIN_RISK_LEVEL_FOR_NOTIFICATION", 9))

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "riesgos")
RETRY_INTERVAL = int(os.getenv("RETRY_INTERVAL", 5))
