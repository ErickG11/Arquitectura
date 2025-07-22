# app/services/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Dict

class IReportGenerator(ABC):
    """
    Interfaz que define el contrato para generar un reporte PDF.
    """
    @abstractmethod
    def generate(self,
                 activos: List[Dict],
                 riesgos: List[Dict],
                 fecha: str,
                 autor: str) -> str:
        """
        Debe generar (o descargar) un PDF con los datos y devolver
        la ruta absoluta al archivo en disco.
        """
        pass
