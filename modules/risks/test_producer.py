import pika
import json

def publicar_mensaje():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='riesgos_criticos')
    mensaje = {"test": "mensaje de prueba desde producer"}
    channel.basic_publish(exchange='', routing_key='riesgos_criticos', body=json.dumps(mensaje))
    print("Mensaje enviado:", mensaje)
    connection.close()

if __name__ == "__main__":
    publicar_mensaje()
