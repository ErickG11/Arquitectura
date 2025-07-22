# app/services/http_report_generator.py
import os
import json
import requests
from datetime import datetime
from flask import current_app
from .interfaces import IReportGenerator

class HTTPReportGenerator(IReportGenerator):
    """
    Implementación de IReportGenerator que llama al microservicio
    a través de Kong para generar el PDF y lo guarda en static/reports.
    """
    def __init__(self, endpoint_url: str, timeout: int = 15):
        self.endpoint_url = endpoint_url
        self.timeout = timeout

    def generate(self,
                 activos: list[dict],
                 riesgos: list[dict],
                 fecha: str,
                 autor: str) -> str:
        # Llamada al microservicio vía Kong
        response = requests.post(
            self.endpoint_url,
            data={
                "activos": json.dumps(activos),
                "riesgos": json.dumps(riesgos),
                "fecha": fecha,
                "autor": autor
            },
            timeout=self.timeout
        )
        response.raise_for_status()

        # Validar que recibimos un PDF
        content_type = response.headers.get("content-type", "")
        if "application/pdf" not in content_type or not response.content:
            raise RuntimeError("Respuesta inválida del generador de PDF")

        # Guardar en static/reports
        reports_dir = os.path.join(current_app.root_path, "static", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        filename = f"informe_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        full_path = os.path.join(reports_dir, filename)

        with open(full_path, "wb") as f:
            f.write(response.content)

        return full_path
