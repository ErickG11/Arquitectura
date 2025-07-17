import os
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generar_pdf(activos: list[dict], riesgos: list[dict], fecha: str, autor: str) -> str:
    tmp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(tmp_dir, "informe_ciber_riesgos.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    w, h = letter

    # Portada
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w / 2, h - 72, "Informe de Gestión de Riesgos")
    c.setFont("Helvetica", 10)
    c.drawString(50, h - 100, f"Fecha: {fecha}")
    c.drawString(50, h - 115, f"Autor: {autor}")
    c.showPage()

    # 1. Inventario de Activos
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h - 50, "1. Inventario de Activos")
    c.setFont("Helvetica", 10)
    y = h - 80

    for a in activos:
        val = round((a["confidencialidad"] + a["integridad"] + a["disponibilidad"]) / 3, 2)
        tipo = a.get("tipo", "-")
        c.drawString(50, y, f"{a['id']}. {a['nombre']} ({tipo})")
        y -= 15
        c.drawString(70, y, f"C: {a['confidencialidad']}   I: {a['integridad']}   D: {a['disponibilidad']}   => Valor Crítico: {val}")
        y -= 20
        if y < 60:
            c.showPage(); y = h - 50

    # 2. Detalle de Riesgos
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h - 50, "2. Detalle de Riesgos")
    c.setFont("Helvetica", 10)
    y = h - 80
    for r in riesgos:
        nivel = r["probabilidad"] * r["impacto"]
        c.drawString(50, y, f"Riesgo {r['id']}: {r['amenaza']}")
        y -= 15
        c.drawString(70, y, f"Activo: {r['activo_nombre']}   Prob: {r['probabilidad']}   Imp: {r['impacto']}   Nivel: {nivel}")
        y -= 20
        if y < 60:
            c.showPage(); y = h - 50

    # 3. Conclusiones y Recomendaciones
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h - 50, "3. Conclusiones y Recomendaciones")
    c.setFont("Helvetica", 10)
    y = h - 80
    c.drawString(50, y, f"- Total de activos: {len(activos)}")
    y -= 15
    c.drawString(50, y, f"- Total de riesgos identificados: {len(riesgos)}")
    y -= 15
    c.drawString(50, y, "- Revisar periódicamente los controles de seguridad.")
    y -= 15
    c.drawString(50, y, "- Priorizar los activos con alto valor crítico.")
    y -= 15
    c.drawString(50, y, "- Atender riesgos con nivel crítico primero.")
    c.save()

    return pdf_path
