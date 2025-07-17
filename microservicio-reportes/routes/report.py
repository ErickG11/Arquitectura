from fastapi import APIRouter, Form
from fastapi.responses import FileResponse
import json
from services.pdf_generator import generar_pdf

report_router = APIRouter()

@report_router.post("/generate")
async def generar_reporte(
    activos: str = Form(...),
    riesgos: str = Form(...),
    fecha: str = Form(...),
    autor: str = Form(...)
):
    activos = json.loads(activos)
    riesgos = json.loads(riesgos)
    pdf_path = generar_pdf(activos, riesgos, fecha, autor)
    return FileResponse(pdf_path, media_type="application/pdf", filename="informe_ciber_riesgos.pdf")
