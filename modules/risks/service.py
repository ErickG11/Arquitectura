from modules.db import SessionLocal
from modules.risks.models import Risk
import pika, json # Mantener importaciones aquí para la función

def lista_riesgos() -> list[dict]:
    """
    Obtiene y devuelve una lista de todos los riesgos de la base de datos.
    """
    session = SessionLocal()
    rows = session.query(Risk).all()
    result = [r.to_dict() for r in rows]
    session.close()
    return result

def publicar_evento_riesgo_critico(riesgo_dict):
    """
    Publica un evento de riesgo crítico en la cola de RabbitMQ.
    """
    connection = None
    try:
        # Conectar a RabbitMQ. 'rabbitmq' es el nombre del servicio en docker-compose.
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        # DECLARACIÓN DE LA COLA: Asegurarse de que 'durable=True' coincida con el consumidor
        # Si la cola ya existe como durable=True, esta declaración funcionará.
        # Si la cola no existe, la creará como durable=True.
        channel.queue_declare(queue='riesgos', durable=True) # <-- CORRECCIÓN AQUI

        # Publicar el mensaje en la cola 'riesgos'
        channel.basic_publish(
            exchange='',
            routing_key='riesgos',
            body=json.dumps(riesgo_dict) # Convertir el diccionario a JSON string
        )
        print(f"[Monolito] Evento de riesgo publicado en RabbitMQ: {riesgo_dict.get('amenaza')}")

    except pika.exceptions.AMQPConnectionError as e:
        print(f"[ERROR] No se pudo conectar a RabbitMQ: {e}")
    except Exception as e:
        print(f"[ERROR] Error al publicar evento en RabbitMQ: {e}")
    finally:
        if connection and connection.is_open:
            connection.close()
            print("[Monolito] Conexión a RabbitMQ cerrada.")


def crear_riesgo(form: dict) -> None:
    """
    Crea un nuevo riesgo en la base de datos y, si es crítico, publica un evento.
    """
    probabilidad = int(form["probabilidad"])
    impacto = int(form["impacto"])
    
    session = SessionLocal()
    try:
        r = Risk(
            amenaza        = form["amenaza"],
            vulnerabilidad = form["vulnerabilidad"],
            probabilidad   = probabilidad,
            impacto        = impacto,
            activo_id      = int(form["activo_id"])
        )
        session.add(r)
        session.commit()
        session.refresh(r) # Refrescar el objeto para obtener el ID y otros campos generados
        
        riesgo_dict = r.to_dict() # Convertir el objeto a diccionario para RabbitMQ
        print(f"[Monolito] Riesgo '{riesgo_dict.get('amenaza')}' guardado en DB con ID: {riesgo_dict.get('id')}")

        # Define umbral crítico
        nivel = probabilidad * impacto
        UMBRAL_CRITICO = 15 # O ajusta según tu análisis, 9 sería 3x3

        # Solo publica si el riesgo es crítico
        if nivel >= UMBRAL_CRITICO:
            publicar_evento_riesgo_critico(riesgo_dict)
        else:
            print(f"[Monolito] Riesgo con nivel {nivel} (no crítico, umbral {UMBRAL_CRITICO}). No se publica evento.")

    except Exception as e:
        session.rollback() # Revertir la transacción si hay un error
        print(f"[ERROR] Error al crear o procesar el riesgo: {e}")
    finally:
        session.close()