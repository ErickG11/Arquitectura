# modules/risks/routes.py
from flask import Blueprint, request, render_template, redirect, url_for
from modules.db             import SessionLocal
from modules.risks.service  import lista_riesgos, crear_riesgo
from modules.assets.models  import Asset

risks_bp = Blueprint(
    "risks",
    __name__,
    template_folder="../../templates"
)

@risks_bp.route("/", methods=["GET", "POST"])
def list_risks_page():
    session = SessionLocal()
    activos = session.query(Asset).all()
    session.close()

    if request.method == "POST":
        crear_riesgo(request.form)
        return redirect(url_for("risks.list_risks_page"))

    riesgos = lista_riesgos()
    return render_template(
      "risks_list.html",
      riesgos=riesgos,
      assets=activos     # <-- for the dropdown
    )
