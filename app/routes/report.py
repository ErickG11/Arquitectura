from flask import Blueprint, render_template, request, send_file, current_app
import json, os
from datetime import datetime
from app.services.http_report_generator import HTTPReportGenerator
from app.services.report_service import ReportService

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
    return render_template("report.html", activos=activos, riesgos=riesgos, fecha=fecha, autor=autor)

@report_bp.route("/download", methods=["GET"])
def report_download():
    activos = json.loads(request.args.get("activos", "[]"))
    riesgos = json.loads(request.args.get("riesgos", "[]"))
    fecha   = request.args.get("fecha", "")
    autor   = request.args.get("autor", "")

    endpoint = current_app.config['REPORT_MICROSERVICE_URL']
    generator = HTTPReportGenerator(endpoint_url=endpoint)
    service   = ReportService(generator)

    try:
        pdf_path = service.generar_pdf(activos, riesgos, fecha, autor)
    except Exception as e:
        current_app.logger.error(f"Error generando PDF: {e}")
        return "Error generando el reporte", 500

    if not os.path.isfile(pdf_path):
        current_app.logger.error(f"PDF no encontrado en: {pdf_path}")
        return "Error generando el reporte", 500

    return send_file(pdf_path, as_attachment=True,
                     download_name=f"reporte_{fecha or datetime.now().strftime('%Y%m%d')}.pdf",
                     mimetype="application/pdf")
