# modules/risks/service.py
from modules.db        import SessionLocal
from modules.risks.models import Risk

def lista_riesgos() -> list[dict]:
    session = SessionLocal()
    rows    = session.query(Risk).all()
    result  = [r.to_dict() for r in rows]
    session.close()
    return result

def crear_riesgo(form: dict) -> None:
    session = SessionLocal()
    r = Risk(
        amenaza        = form["amenaza"],
        vulnerabilidad = form["vulnerabilidad"],
        probabilidad   = int(form["probabilidad"]),
        impacto        = int(form["impacto"]),
        activo_id      = int(form["activo_id"])
    )
    session.add(r)
    session.commit()
    session.close()
