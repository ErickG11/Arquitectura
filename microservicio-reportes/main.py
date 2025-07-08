from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = FastAPI()

class ReportRequest(BaseModel):
    activos: list
    riesgos: list

@app.post("/report")
async def generar_report(data: ReportRequest):
    pdf_path = "informe_ciber_riesgos.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    w, h = letter
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w/2, h-72, "Informe de Gestión de Riesgos")
    c.setFont("Helvetica", 10)
    c.drawString(50, h-100, f"Activos: {len(data.activos)}, Riesgos: {len(data.riesgos)}")
    c.showPage()
    c.save()
    return FileResponse(pdf_path, filename=pdf_path, media_type='application/pdf')
