from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import tempfile
import json

app = FastAPI()

@app.post("/report/generate")
async def generar_reporte(
    activos: str = Form(...),
    riesgos: str = Form(...),
    fecha: str = Form(...),
    autor: str = Form(...),
):
    activos = json.loads(activos)
    riesgos = json.loads(riesgos)

    tmp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(tmp_dir, "informe_ciber_riesgos.pdf")

    c = canvas.Canvas(pdf_path, pagesize=letter)
    w, h = letter

    # Portada
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w/2, h-72, "Informe de Gestión de Riesgos")
    c.setFont("Helvetica", 10)
    c.drawString(50, h-100, f"Fecha: {fecha}")
    c.drawString(50, h-115, f"Autor: {autor}")
    c.showPage()

    # Inventario de Activos
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h-50, "1. Inventario de Activos")
    c.setFont("Helvetica", 10)
    y = h-80
    for a in activos:
        val = round((a["confidencialidad"] + a["integridad"] + a["disponibilidad"])/3, 2)
        tipo = a.get("tipo", "-")
        c.drawString(50, y, f"{a['id']}. {a['nombre']} ({tipo}) — Valor = {val}")
        y -= 15
        if y < 50:
            c.showPage(); y = h-50

    # Detalle Riesgos
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h-50, "2. Detalle de Riesgos")
    c.setFont("Helvetica", 10)
    y = h-80
    for r in riesgos:
        nivel = r["probabilidad"] * r["impacto"]
        c.drawString(50, y, f"Riesgo {r['id']}: {r['amenaza']} — Activo: {r['activo_nombre']} — Nivel: {nivel}")
        y -= 15
        if y < 50:
            c.showPage(); y = h-50

    # Conclusiones
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h-50, "3. Conclusiones y Recomendaciones")
    c.setFont("Helvetica", 10)
    c.drawString(50, h-80, f"- Activos: {len(activos)}, Riesgos: {len(riesgos)}")
    c.drawString(50, h-95, "- Revisar controles periódicamente")
    c.save()

    return FileResponse(pdf_path, media_type="application/pdf", filename="informe_ciber_riesgos.pdf")
