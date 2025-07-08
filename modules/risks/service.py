from modules.db        import SessionLocal
from modules.risks.models import Risk

def lista_riesgos() -> list[dict]:
    session = SessionLocal()
    rows    = session.query(Risk).all()
    result  = [r.to_dict() for r in rows]
    session.close()
    return result

import pika, json

def publicar_evento_riesgo_critico(riesgo_dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='riesgos')
    channel.basic_publish(
        exchange='',
        routing_key='riesgos',
        body=json.dumps(riesgo_dict)
    )
    connection.close()

def crear_riesgo(form: dict) -> None:
    probabilidad = int(form["probabilidad"])
    impacto      = int(form["impacto"])
    session = SessionLocal()
    r = Risk(
        amenaza        = form["amenaza"],
        vulnerabilidad = form["vulnerabilidad"],
        probabilidad   = probabilidad,
        impacto        = impacto,
        activo_id      = int(form["activo_id"])
    )
    session.add(r)
    session.commit()

    # Creamos el diccionario ANTES de cerrar la sesión
    riesgo_dict = r.to_dict()
    session.close()

    # Publica siempre al crear un riesgo
    publicar_evento_riesgo_critico(riesgo_dict)

