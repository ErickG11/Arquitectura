# modules/catalog/models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm  import relationship
from modules.db      import Base
from modules.assets.models import asset_business_unit, asset_label

class User(Base):
    __tablename__ = "users"
    id        = Column(Integer, primary_key=True, index=True)
    username  = Column(String(50),  nullable=False, unique=True)
    full_name = Column(String(100), nullable=False)

    assets    = relationship("Asset", back_populates="owner")


class BusinessUnit(Base):
    __tablename__ = "business_units"
    id    = Column(Integer, primary_key=True, index=True)
    name  = Column(String(100), nullable=False)

    # La relación M2M con Asset
    assets = relationship(
        "Asset",
        secondary=asset_business_unit,
        back_populates="business_units"
    )


class Label(Base):
    __tablename__ = "labels"
    id    = Column(Integer, primary_key=True, index=True)
    name  = Column(String(100), nullable=False)

    # La relación M2M con Asset
    assets = relationship(
        "Asset",
        secondary=asset_label,
        back_populates="labels"
    )
