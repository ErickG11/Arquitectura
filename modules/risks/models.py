# modules/risks/models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm    import relationship
from modules.db        import Base

class Risk(Base):
    __tablename__    = "riesgos"
    id               = Column(Integer, primary_key=True, index=True)
    amenaza          = Column(String(200), nullable=False)
    vulnerabilidad   = Column(String(200), nullable=False)
    probabilidad     = Column(Integer, nullable=False)
    impacto          = Column(Integer, nullable=False)
    activo_id        = Column(Integer, ForeignKey("activos.id"), nullable=False)

    # ← this must exactly match Asset.riesgos
    activo = relationship(
        "Asset",
        back_populates="riesgos"
    )

    def to_dict(self):
        return {
            "id":             self.id,
            "amenaza":        self.amenaza,
            "vulnerabilidad": self.vulnerabilidad,
            "probabilidad":   self.probabilidad,
            "impacto":        self.impacto,
            "activo_id":      self.activo_id,
            "activo_nombre":  self.activo.nombre if self.activo else None,
        }
