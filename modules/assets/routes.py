# modules/assets/routes.py
from flask import Blueprint, request, render_template, redirect, url_for
from modules.db import SessionLocal

# IMPORTS CORRECTOS: User, BU y Label desde catalog.models
from modules.catalog.models import User, BusinessUnit, Label

# Servicios de activos
from modules.assets.service import (
    lista_activos,
    crear_activo,
    get_asset,
    update_asset,
    eliminar_activo,
)

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

    # para el modal de creación/editado
    session = SessionLocal()
    users          = session.query(User).all()
    business_units = session.query(BusinessUnit).all()
    labels         = session.query(Label).all()
    session.close()

    return render_template(
        "assets_list.html",
        activos=activos,
        users=users,
        business_units=business_units,
        labels=labels,
    )

@assets_bp.route("/edit/<int:asset_id>", methods=["GET", "POST"])
def edit_asset_page(asset_id):
    # datos para los selects
    session = SessionLocal()
    users          = session.query(User).all()
    business_units = session.query(BusinessUnit).all()
    labels         = session.query(Label).all()
    session.close()

    if request.method == "POST":
        update_asset(asset_id, request.form)
        return redirect(url_for("assets.get_all_assets_page"))

    activo = get_asset(asset_id)
    if not activo:
        return redirect(url_for("assets.get_all_assets_page"))

    return render_template(
        "assets_edit.html",
        activo=activo,
        users=users,
        business_units=business_units,
        labels=labels,
    )

@assets_bp.route("/delete/<int:asset_id>", methods=["POST"])
def delete_asset(asset_id):
    eliminar_activo(asset_id)
    return redirect(url_for("assets.get_all_assets_page"))
