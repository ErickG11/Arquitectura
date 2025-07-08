from fastapi import FastAPI
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = FastAPI()

# Simula obtener activos y riesgos desde una DB o API
def obtener_activos():
    return [
        {"id": 1, "nombre": "Servidor 1", "confidencialidad": 5, "integridad": 4, "disponibilidad": 5},
        {"id": 2, "nombre": "Base de datos", "confidencialidad": 5, "integridad": 5, "disponibilidad": 4},
    ]

def obtener_riesgos():
    return [
        {"id": 1, "amenaza": "Malware", "probabilidad": 4, "impacto": 5, "activo_nombre": "Servidor 1"},
        {"id": 2, "amenaza": "Falla hardware", "probabilidad": 3, "impacto": 4, "activo_nombre": "Base de datos"},
    ]

@app.get("/report")
def descargar_reporte():
    pdf_path = "informe_ciber_riesgos.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    w, h = letter

    activos = obtener_activos()
    riesgos = obtener_riesgos()

    # Portada
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w/2, h-72, "Informe de Gestión de Riesgos")
    c.setFont("Helvetica", 10)
    c.drawString(50, h-100, f"Total Activos: {len(activos)}")
    c.drawString(50, h-115, f"Total Riesgos: {len(riesgos)}")
    c.showPage()

    # Inventario activos
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h-50, "Inventario de Activos")
    c.setFont("Helvetica", 10)
    y = h - 80
    for a in activos:
        val = round((a["confidencialidad"] + a["integridad"] + a["disponibilidad"]) / 3, 2)
        c.drawString(50, y, f"{a['id']}. {a['nombre']} — Valor Crítico: {val}")
        y -= 15
        if y < 50:
            c.showPage()
            y = h - 50

    # Detalle riesgos
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h-50, "Detalle de Riesgos")
    c.setFont("Helvetica", 10)
    y = h - 80
    for r in riesgos:
        nivel = r["probabilidad"] * r["impacto"]
        c.drawString(50, y, f"{r['id']}. {r['amenaza']} — Activo: {r['activo_nombre']} — Nivel: {nivel}")
        y -= 15
        if y < 50:
            c.showPage()
            y = h - 50

    c.save()

    return FileResponse(pdf_path, media_type='application/pdf', filename="informe_ciber_riesgos.pdf")
