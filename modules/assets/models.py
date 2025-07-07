# modules/assets/models.py

from sqlalchemy import (
    Column, Integer, String, ForeignKey, Table
)
from sqlalchemy.orm import relationship
from modules.db import Base  # tu Base compartido

# Tablas intermedias M2M
asset_business_unit = Table(
    "asset_business_unit",
    Base.metadata,
    Column("asset_id", Integer, ForeignKey("activos.id"), primary_key=True),
    Column("business_unit_id", Integer, ForeignKey("business_units.id"), primary_key=True),
)

asset_label = Table(
    "asset_label",
    Base.metadata,
    Column("asset_id", Integer, ForeignKey("activos.id"), primary_key=True),
    Column("label_id", Integer, ForeignKey("labels.id"), primary_key=True),
)

class Asset(Base):
    __tablename__ = "activos"

    id               = Column(Integer, primary_key=True, index=True)
    nombre           = Column(String(100), nullable=False)
    tipo             = Column(String(50),  nullable=False)
    confidencialidad = Column(Integer,    nullable=False)
    integridad       = Column(Integer,    nullable=False)
    disponibilidad   = Column(Integer,    nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner    = relationship("User",   back_populates="assets")

    # relación uno a muchos con Risk (en modules/risks/models.py)
    riesgos  = relationship("Risk", back_populates="activo", cascade="all, delete-orphan")

    # relaciones M2M
    business_units = relationship(
        "BusinessUnit",
        secondary=asset_business_unit,
        back_populates="assets"
    )
    labels = relationship(
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
            "owner": {
                "id": self.owner.id,
                "name": self.owner.full_name
            } if self.owner else None,
            "business_units": [bu.name for bu in self.business_units],
            "labels": [lbl.name for lbl in self.labels],
            "num_riesgos": len(self.riesgos),
        }

class User(Base):
    __tablename__ = "users"

    id        = Column(Integer, primary_key=True, index=True)
    username  = Column(String(50),  nullable=False, unique=True)
    full_name = Column(String(100), nullable=False)

    assets = relationship("Asset", back_populates="owner")

class BusinessUnit(Base):
    __tablename__ = "business_units"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    assets = relationship(
        "Asset",
        secondary=asset_business_unit,
        back_populates="business_units"
    )

class Label(Base):
    __tablename__ = "labels"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    assets = relationship(
        "Asset",
        secondary=asset_label,
        back_populates="labels"
    )
