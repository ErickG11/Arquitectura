# modules/catalog/models.py

from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Reutilizamos tu cadena de conexión
CONN_STR = (
    "mssql+pyodbc://@localhost/CiberRiesgosDB"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
)
engine = create_engine(CONN_STR, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Threat(Base):
    __tablename__ = "threats"
    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)


class Control(Base):
    __tablename__ = "controls"
    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)


class User(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    full_name= Column(String(100), nullable=False)

# Crea todas las tablas (catálogos + las tuyas existentes)
Base.metadata.create_all(bind=engine)
