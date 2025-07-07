# modules/assets/service.py

from modules.db import SessionLocal
from modules.assets.models import Asset

def lista_activos() -> list[dict]:
    session = SessionLocal()
    rows = session.query(Asset).all()
    result = [a.to_dict() for a in rows]
    session.close()
    return result

def crear_activo(form: dict) -> None:
    session = SessionLocal()
    a = Asset(
        nombre           = form["nombre"],
        tipo             = form["tipo"],
        confidencialidad = int(form["confidencialidad"]),
        integridad       = int(form["integridad"]),
        disponibilidad   = int(form["disponibilidad"]),
        owner_id         = int(form["owner_id"]) if form.get("owner_id") else None
    )
    session.add(a)
    session.commit()
    session.close()

def eliminar_activo(asset_id: int) -> None:
    session = SessionLocal()
    a = session.get(Asset, asset_id)
    if a:
        session.delete(a)
        session.commit()
    session.close()
