# app/services/report_tools.py
import os, json, requests
from datetime import datetime
from flask import current_app

def generar_pdf(activos, riesgos, fecha, autor, url):
    response = requests.post(
        url,
        data={
            "activos": json.dumps(activos),
            "riesgos": json.dumps(riesgos),
            "fecha": fecha,
            "autor": autor
        },
        timeout=15
    )
    response.raise_for_status()
    # Guarda el PDF
    reports_dir = os.path.join(current_app.root_path, "static", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    filename = f"informe_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    full_path = os.path.join(reports_dir, filename)
    with open(full_path, "wb") as f:
        f.write(response.content)
    return full_path
