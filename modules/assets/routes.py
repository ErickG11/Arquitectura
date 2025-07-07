from flask import Blueprint, request, render_template, redirect, url_for
from modules.assets.service import lista_activos, crear_activo, eliminar_activo
from modules.assets.models  import User, BusinessUnit, Label
from modules.db            import SessionLocal

assets_bp = Blueprint(
    "assets",
    __name__,
    template_folder="../../templates"
)

@assets_bp.route("/", methods=["GET", "POST"])
def get_all_assets_page():
    if request.method == "POST":
        crear_activo(request.form)
        return redirect(url_for("assets.get_all_assets_page"))

    activos = lista_activos()
    session = SessionLocal()
    users   = session.query(User).all()
    units   = session.query(BusinessUnit).all()
    labels  = session.query(Label).all()
    session.close()

    return render_template(
      "assets_list.html",
      activos=activos,
      users=users,
      business_units=units,
      labels=labels
    )

@assets_bp.route("/delete/<int:asset_id>", methods=["GET","POST"])
def delete_asset(asset_id):
    eliminar_activo(asset_id)
    return redirect(url_for("assets.get_all_assets_page"))
