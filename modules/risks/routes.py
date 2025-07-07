# modules/risks/routes.py

from flask import Blueprint, request, render_template, redirect, url_for
from modules.risks.service import lista_riesgos, crear_riesgo
from modules.assets.service import lista_activos

risks_bp = Blueprint(
    "risks", __name__,
    template_folder="../../templates"
)

@risks_bp.route("/", methods=["GET","POST"])
def list_risks_page():
    if request.method == "POST":
        crear_riesgo(request.form)
        return redirect(url_for("risks.list_risks_page"))

    riesgos = lista_riesgos()
    activos = lista_activos()   # <-- aquí lo llamamos 'activos', no 'assets'
    return render_template(
        "risks_list.html",
        riesgos=riesgos,
        activos=activos        # <— pasa la lista como 'activos'
    )
