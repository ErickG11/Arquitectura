import os, json, requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from flask import current_app

def generar_charts(activos):
    chart_dir = os.path.join(current_app.root_path, "static", "charts")
    os.makedirs(chart_dir, exist_ok=True)

    names = [a["nombre"] for a in activos]
    values = [round((a["confidencialidad"] + a["integridad"] + a["disponibilidad"]) / 3, 2) for a in activos]

    plt.figure(figsize=(10, 5))
    plt.bar(names, values, color="skyblue")
    plt.title("Valor Crítico de Activos")
    plt.ylabel("Valor")
    plt.xticks(rotation=45, ha='right')

    path = os.path.join(chart_dir, "asset_values.png")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return "/static/charts/asset_values.png"

def generar_matriz(riesgos: list[dict]) -> str:
    if not riesgos:
        return ""
    mat = np.zeros((5, 5), dtype=int)
    for r in riesgos:
        try:
            p = max(0, min(4, int(r.get("probabilidad", 1)) - 1))
            i = max(0, min(4, int(r.get("impacto", 1)) - 1))
            mat[4 - i, p] += 1
        except:
            continue
    fig, ax = plt.subplots(figsize=(7,7))
    masked = np.ma.masked_equal(mat, 0)
    im = ax.imshow(masked, origin="lower", cmap="Reds")
    fig.colorbar(im, ax=ax, shrink=0.7)

    chart_dir = os.path.join(current_app.root_path, "static", "charts")
    os.makedirs(chart_dir, exist_ok=True)
    path = os.path.join(chart_dir, "risk_matrix.png")

    fig.savefig(path, dpi=150)
    plt.close(fig)
    return "/static/charts/risk_matrix.png"

def generar_pdf(activos, riesgos, fecha, autor, url):
    try:
        print(f"[DEBUG] Llamando a {url} con activos={len(activos)}, riesgos={len(riesgos)}")
        response = requests.post(
            url,
            data={
                "activos": json.dumps(activos),
                "riesgos": json.dumps(riesgos),
                "fecha": fecha,
                "autor": autor,
            },
            timeout=15
        )
        print("[DEBUG] Status code:", response.status_code)
        print("[DEBUG] Content-Type:", response.headers.get("content-type"))
        print("[DEBUG] Content-Length:", len(response.content))

        response.raise_for_status()

        # Baja el umbral para ver si el PDF es pequeño
        if not response.content:
            print("[ERROR] Respuesta vacía")
            return None

        # Ruta robusta y compatible con Docker
        reports_dir = os.path.join(current_app.root_path, "static", "reports")
        os.makedirs(reports_dir, exist_ok=True)

        filename = f"informe_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        full_path = os.path.join(reports_dir, filename)
        
        with open(full_path, "wb") as f:
            f.write(response.content)

        return full_path
    except Exception as e:
        print(f"[ERROR] al generar PDF: {e}")
        return None
