# modules/assets/service.py

from modules.db import SessionLocal
from modules.assets.models import Asset
from modules.catalog.models import BusinessUnit, Label
from modules.risks.models   import Risk

def lista_activos() -> list[dict]:
    session = SessionLocal()
    rows    = session.query(Asset).all()
    result  = [a.to_dict() for a in rows]
    session.close()
    return result

def get_asset(asset_id: int) -> Asset | None:
    session = SessionLocal()
    a = session.query(Asset).get(asset_id)
    session.close()
    return a

def crear_activo(form: dict) -> None:
    session = SessionLocal()
    a = Asset(
        nombre           = form["nombre"],
        tipo             = form["tipo"],
        confidencialidad = int(form["confidencialidad"]),
        integridad       = int(form["integridad"]),
        disponibilidad   = int(form["disponibilidad"]),
        owner_id         = form.get("owner_id") or None
    )
    # M2M unidades
    bu_ids = form.getlist("business_units")
    if bu_ids:
        a.business_units = session.query(BusinessUnit).filter(
            BusinessUnit.id.in_(bu_ids)
        ).all()
    # M2M etiquetas
    label_ids = form.getlist("labels")
    if label_ids:
        a.labels = session.query(Label).filter(
            Label.id.in_(label_ids)
        ).all()

    session.add(a)
    session.commit()
    session.close()

def update_asset(asset_id: int, form: dict) -> None:
    session = SessionLocal()
    a = session.query(Asset).get(asset_id)
    if not a:
        session.close()
        return

    a.nombre           = form["nombre"]
    a.tipo             = form["tipo"]
    a.confidencialidad = int(form["confidencialidad"])
    a.integridad       = int(form["integridad"])
    a.disponibilidad   = int(form["disponibilidad"])
    a.owner_id         = form.get("owner_id") or None

    bu_ids = form.getlist("business_units")
    a.business_units = (
        session.query(BusinessUnit).filter(BusinessUnit.id.in_(bu_ids)).all()
        if bu_ids else []
    )
    label_ids = form.getlist("labels")
    a.labels = (
        session.query(Label).filter(Label.id.in_(label_ids)).all()
        if label_ids else []
    )

    session.commit()
    session.close()

def eliminar_activo(asset_id: int) -> None:
    session = SessionLocal()
    session.query(Risk).filter(Risk.activo_id == asset_id).delete(
        synchronize_session=False
    )
    a = session.query(Asset).get(asset_id)
    if a:
        session.delete(a)
        session.commit()
    session.close()
