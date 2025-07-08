import pika
import time
import json

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f"[NOTIFICACIÓN] Riesgo crítico recibido: {data}")
    except Exception as e:
        print(f"[ERROR] Al procesar el mensaje: {e}")

def consumir():
    while True:
        try:
            print("Intentando conectar a RabbitMQ...")
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            print("Conectado a RabbitMQ")
            break
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ no está listo, esperando 5 segundos...")
            time.sleep(5)

    channel = connection.channel()
    channel.queue_declare(queue='riesgos')
    channel.basic_consume(queue='riesgos', on_message_callback=callback, auto_ack=True)
    print('[*] Esperando riesgos críticos. CTRL+C para salir.')
    channel.start_consuming()

if __name__ == "__main__":
    consumir()
