# modules/risks/service.py

from modules.db import SessionLocal
from modules.risks.models import Risk
from modules.assets.models import Asset

def lista_riesgos() -> list[dict]:
    session = SessionLocal()
    rows = session.query(Risk).all()
    result = []
    for r in rows:
        activo = session.get(Asset, r.activo_id)
        result.append({
            "id": r.id,
            "amenaza": r.amenaza,
            "vulnerabilidad": r.vulnerabilidad,
            "probabilidad": r.probabilidad,
            "impacto": r.impacto,
            "activo_id": r.activo_id,
            "activo_nombre": activo.nombre if activo else None,
        })
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
