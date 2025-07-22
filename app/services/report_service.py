# app/services/report_service.py
from typing import List, Dict
from .interfaces import IReportGenerator

class ReportService:
    """
    Servicio que orquesta la generación de reportes usando
    una implementación de IReportGenerator.
    """
    def __init__(self, generator: IReportGenerator):
        self.generator = generator

    def generar_pdf(self,
                    activos: List[Dict],
                    riesgos: List[Dict],
                    fecha: str,
                    autor: str) -> str:
        """
        Devuelve la ruta al PDF generado o lanza excepción si hay fallo.
        """
        return self.generator.generate(activos, riesgos, fecha, autor)
