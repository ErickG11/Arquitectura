import os
from flask       import Flask, render_template, request, redirect, url_for, send_file
import matplotlib.pyplot    as plt
import numpy               as np

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen       import canvas

# 1) Initialize metadata and tables
from modules.db               import Base, engine
import modules.catalog.models 
import modules.assets.models   # registers Asset & User
import modules.risks.models    # registers Risk
Base.metadata.create_all(bind=engine)

# 2) Blueprints and services

from modules.assets.routes    import assets_bp
from modules.risks.routes     import risks_bp
from modules.assets.service   import lista_activos
from modules.risks.service    import lista_riesgos

app = Flask(__name__)
app.register_blueprint(assets_bp, url_prefix="/assets")
app.register_blueprint(risks_bp,  url_prefix="/risks")
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/reports")
def reports():
    return render_template("reports.html")

def generar_charts(activos: list[dict]) -> str:
    nombres = [a["nombre"] for a in activos]
    valores = [(a["confidencialidad"] + a["integridad"] + a["disponibilidad"]) / 3
               for a in activos]
    chart_dir = os.path.join(app.static_folder, "charts")
    os.makedirs(chart_dir, exist_ok=True)

    plt.figure()
    plt.bar(nombres, valores)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    path = os.path.join(chart_dir, "asset_values.png")
    plt.savefig(path)
    plt.close()
    return "/static/charts/asset_values.png"

def generar_matriz(riesgos: list[dict]) -> str:
    mat = np.zeros((5, 5), dtype=int)
    for r in riesgos:
        p = max(1, min(5, int(r["probabilidad"]))) - 1
        i = max(1, min(5, int(r["impacto"]   ))) - 1
        mat[4 - i, p] += 1

    masked = np.ma.masked_equal(mat, 0)
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_facecolor("#f0f0f0")
    im = ax.imshow(masked, origin="lower", interpolation="none",
                   cmap="Reds", vmin=1, vmax=mat.max() or 1)
    fig.colorbar(im, ax=ax, shrink=0.8, label="# Riesgos")
    ax.set_xticks(np.arange(-.5, 5, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 5, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_xticks(range(5)); ax.set_yticks(range(5))
    ax.set_xticklabels([1,2,3,4,5]); ax.set_yticklabels(list(reversed([1,2,3,4,5])))
    ax.set_xlabel("Probabilidad"); ax.set_ylabel("Impacto")
    ax.set_title("Matriz de Riesgo Global")
    for (row, col), val in np.ndenumerate(mat):
        if val > 0:
            ax.text(col, row, str(val), ha="center", va="center",
                    color="black", fontweight="bold")
    plt.tight_layout()
    chart_dir = os.path.join(app.static_folder, "charts")
    os.makedirs(chart_dir, exist_ok=True)
    path = os.path.join(chart_dir, "risk_matrix.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return "/static/charts/risk_matrix.png"

@app.route("/reports/view")
def report_view():
    activos = lista_activos()
    riesgos = lista_riesgos()
    return render_template(
        "report.html",
        fecha="2025-07-06",
        autor="Usuario",
        activos=activos,
        riesgos=riesgos,
        chart_asset=generar_charts(activos),
        chart_matrix=generar_matriz(riesgos),
    )

@app.route("/reports/download")
def report_download():
    activos = lista_activos()
    riesgos = lista_riesgos()
    img1 = generar_charts(activos)
    img2 = generar_matriz(riesgos)

    pdf_dir  = os.path.join(app.static_folder, "reports")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, "informe_ciber_riesgos.pdf")

    c = canvas.Canvas(pdf_path, pagesize=letter)
    w, h = letter

    # Portada
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w/2, h-72, "Informe de Gestión de Riesgos")
    c.setFont("Helvetica", 10)
    c.drawString(50, h-100, f"Fecha: 2025-07-06")
    c.drawString(50, h-115, "Autor: Usuario")
    c.showPage()

    # Inventario
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h-50, "1. Inventario de Activos")
    c.setFont("Helvetica", 10)
    y = h-80
    for a in activos:
        val = round((a["confidencialidad"] + a["integridad"] + a["disponibilidad"])/3, 2)
        c.drawString(50, y, f"{a['id']}. {a['nombre']} ({a['tipo']}) — Valor = {val}")
        y -= 15
        if y < 50:
            c.showPage(); y = h-50

    # Gráficos
    c.showPage()
    p1 = os.path.join(app.static_folder, img1.lstrip("/"))
    if os.path.exists(p1): c.drawImage(p1, 50, 300, width=500, preserveAspectRatio=True)
    c.showPage()
    p2 = os.path.join(app.static_folder, img2.lstrip("/"))
    if os.path.exists(p2): c.drawImage(p2, 50, 200, width=500, preserveAspectRatio=True)

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

    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
