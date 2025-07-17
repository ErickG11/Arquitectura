import pika
import time
from config import settings
from consumer.callback import process_risk_message

def start_consuming():
    while True:
        try:
            print(f"Conectando a RabbitMQ en {settings.RABBITMQ_HOST}...")
            connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)

            def callback(ch, method, properties, body):
                process_risk_message(body)

            channel.basic_consume(queue=settings.RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=True)
            print(f"[*] Escuchando en la cola '{settings.RABBITMQ_QUEUE}'...")
            channel.start_consuming()
        except Exception as e:
            print(f"[ERROR] Fallo en conexión. Reintentando en {settings.RETRY_INTERVAL}s. Error: {e}")
            time.sleep(settings.RETRY_INTERVAL)
