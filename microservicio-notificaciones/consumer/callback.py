import json
from mailer.sender import send_notification_email
from config import settings

def process_risk_message(body):
    try:
        data = json.loads(body)
        amenaza = data.get("amenaza", "N/A")
        probabilidad = data.get("probabilidad", 0)
        impacto = data.get("impacto", 0)
        nivel = probabilidad * impacto
        activo_afectado = data.get("activo_nombre", "Desconocido")

        print(f"\n[NOTIFICACIÓN] Riesgo recibido:")
        print(json.dumps(data, indent=2))

        if nivel >= settings.MIN_RISK_LEVEL_FOR_NOTIFICATION:
            subject = f"ALERTA: Riesgo '{amenaza}' en '{activo_afectado}' (Nivel: {nivel})"
            body = (
                f"Amenaza: {amenaza}\n"
                f"Activo: {activo_afectado}\n"
                f"Probabilidad: {probabilidad}\n"
                f"Impacto: {impacto}\n"
                f"Nivel: {nivel}\n\n"
                f"Detalles:\n{json.dumps(data, indent=2)}"
            )
            send_notification_email(subject, body, settings.NOTIFICATION_RECIPIENT)
        else:
            print(f"[INFO] Nivel de riesgo {nivel} no requiere notificación.")
    except Exception as e:
        print(f"[ERROR] Fallo al procesar mensaje: {e}")
