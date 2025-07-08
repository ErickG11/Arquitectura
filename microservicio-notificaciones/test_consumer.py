import pika
import json

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"[NOTIFICACIÓN] Mensaje recibido: {data}")

def consumir():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='riesgos_criticos')
    channel.basic_consume(queue='riesgos_criticos', on_message_callback=callback, auto_ack=True)
    print('[*] Esperando mensajes en riesgos_criticos. CTRL+C para salir.')
    channel.start_consuming()

if __name__ == "__main__":
    consumir()
