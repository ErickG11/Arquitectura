# modules/db.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Datos de conexión según tu captura
USER = "userpy"
PASSWORD = "12345hola"
SERVER = "192.168.1.250"
DATABASE = "CiberRiesgosDB"
DRIVER = "ODBC+Driver+17+for+SQL+Server"

CONN_STR = (
    "mssql+pyodbc://userpy:12345hola@192.168.1.250:1433/CiberRiesgosDB"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&timeout=30"
)



engine = create_engine(CONN_STR, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()