import smtplib
from email.mime.text import MIMEText
from config import settings

def send_notification_email(subject: str, body: str, recipient: str):
    if settings.EMAIL_PASSWORD == "TU_CONTRASEÑA_DE_APLICACION_DE_16_CARACTERES":
        print("[ERROR] La contraseña no ha sido actualizada.")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_SENDER
    msg["To"] = recipient

    try:
        with smtplib.SMTP(settings.EMAIL_SMTP_SERVER, settings.EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"[EMAIL] Notificación enviada a {recipient}")
    except smtplib.SMTPException as e:
        print(f"[ERROR] Error al enviar correo: {e}")
