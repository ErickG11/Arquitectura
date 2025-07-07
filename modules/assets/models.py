# modules/assets/models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from modules.db import Base  # <-- importas el Base central

class Asset(Base):
    __tablename__ = "activos"
    id               = Column(Integer, primary_key=True, index=True)
    nombre           = Column(String(100), nullable=False)
    tipo             = Column(String(50),  nullable=False)
    confidencialidad = Column(Integer, nullable=False)
    integridad       = Column(Integer, nullable=False)
    disponibilidad   = Column(Integer, nullable=False)
    owner_id         = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner            = relationship("User", back_populates="assets")
    riesgos          = relationship("Risk", back_populates="activo")

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
            } if self.owner else None
        }

class User(Base):
    __tablename__ = "users"
    id        = Column(Integer, primary_key=True, index=True)
    username  = Column(String(50), nullable=False, unique=True)
    full_name = Column(String(100), nullable=False)
    assets    = relationship("Asset", back_populates="owner")

class BusinessUnit(Base):
    __tablename__ = "business_units"
    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

class Label(Base):
    __tablename__ = "labels"
    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
