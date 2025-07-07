from modules.db import SessionLocal
from modules.assets.models import Asset
from modules.risks.models import Risk

def lista_activos() -> list[dict]:
    session = SessionLocal()
    assets = session.query(Asset).all()
    result = []
    for a in assets:
        result.append({
            "id": a.id,
            "nombre": a.nombre,
            "tipo": a.tipo,
            "confidencialidad": a.confidencialidad,
            "integridad": a.integridad,
            "disponibilidad": a.disponibilidad,
            "owner_name": a.owner.full_name if a.owner else "--",
            "num_riesgos": len(a.riesgos),
            "business_units": [bu.name for bu in a.business_units],
            "labels": [lbl.name for lbl in a.labels],
        })
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
        owner_id         = form.get("owner_id") or None
    )
    # Asignar Unidades y Etiquetas si vienen en el form
    if form.getlist("business_units"):
        from modules.assets.models import BusinessUnit
        a.business_units = [ session.query(BusinessUnit).get(int(bu_id))
                             for bu_id in form.getlist("business_units") ]
    if form.getlist("labels"):
        from modules.assets.models import Label
        a.labels = [ session.query(Label).get(int(lbl_id))
                     for lbl_id in form.getlist("labels") ]

    session.add(a)
    session.commit()
    session.close()

def eliminar_activo(asset_id: int) -> None:
    session = SessionLocal()
    # Borrar riesgos huérfanos
    session.query(Risk).filter(Risk.activo_id == asset_id).delete(synchronize_session=False)
    # Borrar el activo
    activo = session.query(Asset).get(asset_id)
    if activo:
        session.delete(activo)
    session.commit()
    session.close()
