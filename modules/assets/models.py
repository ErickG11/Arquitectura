# modules/assets/models.py
from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, Table
)
from sqlalchemy.orm import relationship
from modules.db import Base

# tablas intermedias
asset_business_unit = Table(
    'asset_business_unit', Base.metadata,
    Column('asset_id',           Integer, ForeignKey('activos.id'),          primary_key=True),
    Column('business_unit_id',   Integer, ForeignKey('business_units.id'),   primary_key=True),
)

asset_label = Table(
    'asset_label', Base.metadata,
    Column('asset_id', Integer, ForeignKey('activos.id'),   primary_key=True),
    Column('label_id', Integer, ForeignKey('labels.id'),     primary_key=True),
)

class Asset(Base):
    __tablename__ = "activos"

    id               = Column(Integer, primary_key=True, index=True)
    nombre           = Column(String(100), nullable=False)
    tipo             = Column(String(50),  nullable=False)
    confidencialidad = Column(Integer,     nullable=False)
    integridad       = Column(Integer,     nullable=False)
    disponibilidad   = Column(Integer,     nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner    = relationship("User", back_populates="assets")

    riesgos         = relationship("Risk", back_populates="activo")
    business_units  = relationship(
        "BusinessUnit",
        secondary=asset_business_unit,
        back_populates="assets"
    )
    labels          = relationship(
        "Label",
        secondary=asset_label,
        back_populates="assets"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "confidencialidad": self.confidencialidad,
            "integridad": self.integridad,
            "disponibilidad": self.disponibilidad,
            "owner_name": self.owner.full_name if self.owner else None,
            "num_riesgos": len(self.riesgos),
            "business_units": [bu.name for bu in self.business_units],
            "labels": [tag.name for tag in self.labels],
        }
