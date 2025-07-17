from flask import Blueprint, render_template, request, send_file
import json, os
from datetime import datetime
from app.services.report_tools import generar_pdf

report_bp = Blueprint("report", __name__)

@report_bp.route("/", methods=["GET"])
def reports_page():
    return render_template("reports.html")

@report_bp.route("/view", methods=["GET"])
def report_view():
    activos = json.loads(request.args.get("activos", "[]"))
    riesgos = json.loads(request.args.get("riesgos", "[]"))
    fecha   = request.args.get("fecha", "")
    autor   = request.args.get("autor", "")
    return render_template(
        "report.html",
        activos=activos,
        riesgos=riesgos,
        fecha=fecha,
        autor=autor
    )

@report_bp.route("/download", methods=["GET"])
def report_download():
    activos = json.loads(request.args.get("activos", "[]"))
    riesgos = json.loads(request.args.get("riesgos", "[]"))
    fecha   = request.args.get("fecha", "")
    autor   = request.args.get("autor", "")

    pdf_path = generar_pdf(
        activos=activos,
        riesgos=riesgos,
        fecha=fecha,
        autor=autor,
        url="http://kong:8000/report/generate"
    )
    if not pdf_path or not os.path.isfile(pdf_path):
        return "Error generando el reporte", 500

    # forzamos descarga directa
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"reporte_{fecha or datetime.now().strftime('%Y%m%d')}.pdf",
        mimetype="application/pdf"
    )


