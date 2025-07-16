# microservicio-notificaciones/main.py

import pika
import time
import json
import smtplib
from email.mime.text import MIMEText
import os # Para acceder a variables de entorno

# --- Configuración de Correo Electrónico (obtener de variables de entorno o usar valores por defecto) ---
# Recuerda: EMAIL_PASSWORD debe ser una contraseña de aplicación si usas Gmail con 2FA.
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "grandaerick10@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "yfcg acxf ppwc dgjy") # <-- ¡ACTUALIZA ESTO CON TU CONTRASEÑA REAL!
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", 587))
NOTIFICATION_RECIPIENT = os.getenv("NOTIFICATION_RECIPIENT", "grandaerick04@gmail.com")

# Umbral de nivel de riesgo para enviar notificación por correo
MIN_RISK_LEVEL_FOR_NOTIFICATION = int(os.getenv("MIN_RISK_LEVEL_FOR_NOTIFICATION", 9))

def send_notification_email(subject: str, body: str, recipient: str):
    """
    Envía un correo electrónico de notificación.
    """
    # Validar que las credenciales no sean los valores por defecto si no se han actualizado
    if EMAIL_PASSWORD == "TU_CONTRASEÑA_DE_APLICACION_DE_16_CARACTERES":
        print("[ERROR] La contraseña de correo no ha sido actualizada. No se puede enviar el email.")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = recipient

    try:
        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls() # Habilita la seguridad TLS
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"[EMAIL] Notificación enviada a {recipient} con asunto: '{subject}'")
    except smtplib.SMTPAuthenticationError:
        print("[ERROR] Error de autenticación SMTP. Revisa el email y la contraseña de aplicación. Asegúrate de que la contraseña sea una 'contraseña de aplicación' si usas Gmail con 2FA.")
    except smtplib.SMTPConnectError as e:
        print(f"[ERROR] Error de conexión SMTP al servidor {EMAIL_SMTP_SERVER}:{EMAIL_SMTP_PORT}: {e}")
    except smtplib.SMTPRecipientsRefused as e:
        print(f"[ERROR] El servidor SMTP rechazó los destinatarios: {e}. Revisa el correo del destinatario.")
    except smtplib.SMTPException as e:
        print(f"[ERROR] Error SMTP general al enviar el correo: {e}")
    except Exception as e:
        print(f"[ERROR] Error inesperado al enviar el correo electrónico: {e}")

def callback(ch, method, properties, body):
    """
    Función de callback que se ejecuta cuando se recibe un mensaje de RabbitMQ.
    Procesa el mensaje de riesgo y decide si enviar una notificación por correo.
    """
    try:
        data = json.loads(body)
        amenaza = data.get("amenaza", "N/A")
        probabilidad = data.get("probabilidad", 0)
        impacto = data.get("impacto", 0)
        nivel = probabilidad * impacto
        activo_afectado = data.get("activo_nombre", "Desconocido") # Asumiendo que el monolito envía el nombre del activo

        print(f"\n[NOTIFICACIÓN] Mensaje de riesgo recibido:")
        print(f"  Amenaza: {amenaza}")
        print(f"  Activo Afectado: {activo_afectado}")
        print(f"  Probabilidad: {probabilidad}, Impacto: {impacto}, Nivel: {nivel}")
        print(f"  Detalles del mensaje: {json.dumps(data, indent=2)}")

        # --- Lógica para decidir cuándo enviar notificación (ej: si el nivel es alto) ---
        if nivel >= MIN_RISK_LEVEL_FOR_NOTIFICATION:
            subject = f"ALERTA CRÍTICA: Riesgo '{amenaza}' en '{activo_afectado}' (Nivel: {nivel})"
            email_body = (
                f"Se ha detectado un riesgo crítico en su sistema de gestión de ciber-riesgos:\n\n"
                f"Amenaza: {amenaza}\n"
                f"Activo Afectado: {activo_afectado}\n"
                f"Probabilidad: {probabilidad}\n"
                f"Impacto: {impacto}\n"
                f"Nivel de Riesgo Calculado: {nivel}\n\n"
                f"Detalles completos del evento:\n{json.dumps(data, indent=2)}\n\n"
                f"Por favor, inicie una investigación y tome las medidas correctivas necesarias."
            )
            send_notification_email(subject, email_body, NOTIFICATION_RECIPIENT)
        else:
            print(f"[INFO] Riesgo detectado con nivel {nivel}, que está por debajo del umbral de {MIN_RISK_LEVEL_FOR_NOTIFICATION} para notificación por correo.")

    except json.JSONDecodeError:
        print(f"[ERROR] Mensaje recibido no es un JSON válido o está mal formado: {body.decode()}")
    except KeyError as e:
        print(f"[ERROR] Mensaje JSON incompleto, falta la clave esperada: '{e}'. Contenido: {body.decode()}")
    except Exception as e:
        print(f"[ERROR] Error inesperado al procesar el mensaje: {e}")

def consumir():
    """
    Establece la conexión con RabbitMQ y comienza a consumir mensajes.
    Incluye lógica de reintento para la conexión.
    """
    connection = None
    channel = None
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq") # Usar el nombre del servicio de Docker Compose
    rabbitmq_queue = os.getenv("RABBITMQ_QUEUE", "riesgos")
    retry_interval = int(os.getenv("RETRY_INTERVAL", 5))

    while True:
        try:
            print(f"Intentando conectar a RabbitMQ en {rabbitmq_host}...")
            connection_parameters = pika.ConnectionParameters(rabbitmq_host, retry_delay=retry_interval)
            connection = pika.BlockingConnection(connection_parameters)
            channel = connection.channel()
            channel.queue_declare(queue=rabbitmq_queue, durable=True) # durable=True para persistencia de la cola
            print("Conectado a RabbitMQ y cola declarada.")
            break
        except pika.exceptions.AMQPConnectionError as e:
            print(f"RabbitMQ no está listo o conexión falló ({e}), esperando {retry_interval} segundos...")
            time.sleep(retry_interval)
        except Exception as e:
            print(f"Error inesperado al conectar a RabbitMQ: {e}, esperando {retry_interval} segundos...")
            time.sleep(retry_interval)

    channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=True)
    print(f'[*] Esperando mensajes en la cola "{rabbitmq_queue}". Para salir presiona CTRL+C.')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Deteniendo consumidor de RabbitMQ.")
        channel.stop_consuming()
    except Exception as e:
        print(f"[ERROR] Error durante el consumo de mensajes: {e}")
    finally:
        if connection and connection.is_open:
            connection.close()
            print("Conexión a RabbitMQ cerrada.")

if __name__ == "__main__":
    consumir()
