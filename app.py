# ciber-riesgos-app/app.py

import os
import requests
import json
import redis
import hashlib # Se mantiene si se usa en otras partes del monolito (ej. autenticación)
from datetime import datetime # Para la fecha actual del reporte

from flask import Flask, render_template, request, redirect, url_for, send_file, Response, abort
import matplotlib.pyplot as plt
import numpy as np

# Aunque reportlab ya no genera el PDF aquí, lo mantenemos si se usa en otras partes
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas

# 1) Initialize metadata and tables
from modules.db import Base, engine
import modules.catalog.models
import modules.assets.models  # registers Asset & User
import modules.risks.models   # registers Risk

# Asegurarse de que la base de datos se cree al iniciar la aplicación
Base.metadata.create_all(bind=engine)

# 2) Blueprints and services
from modules.assets.routes import assets_bp
from modules.risks.routes import risks_bp
from modules.assets.service import lista_activos
from modules.risks.service import lista_riesgos

# Inicialización de la aplicación Flask
app = Flask(__name__)
app.register_blueprint(assets_bp, url_prefix="/assets")
app.register_blueprint(risks_bp, url_prefix="/risks")
app.url_map.strict_slashes = False

# --- Configuración de URLs de Microservicios y Redis (desde variables de entorno) ---
REPORT_MICROSERVICE_URL = os.getenv("REPORT_MICROSERVICE_URL", "http://kong:8000/report/generate")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Directorios para archivos generados (relativos a la carpeta static)
CHART_DIR_NAME = "charts"
REPORT_DIR_NAME = "reports"

# Asegurarse de que los directorios para gráficos y reportes existan dentro de static
# Flask ya configura app.static_folder por defecto a 'static' en la raíz del proyecto
chart_output_path = os.path.join(app.static_folder, CHART_DIR_NAME)
report_output_path = os.path.join(app.static_folder, REPORT_DIR_NAME)
os.makedirs(chart_output_path, exist_ok=True)
os.makedirs(report_output_path, exist_ok=True)


# Inicializar Redis
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    r.ping() # Prueba la conexión
    print(f"Conectado a Redis en {REDIS_HOST}:{REDIS_PORT}")
except redis.exceptions.ConnectionError as e:
    print(f"ERROR: No se pudo conectar a Redis en {REDIS_HOST}:{REDIS_PORT}. {e}")
    r = None # Asegurarse de que 'r' sea None si la conexión falla


@app.route("/")
def home():
    """Ruta principal que renderiza la página de inicio."""
    return render_template("index.html")

@app.route("/reports")
def reports():
    """Ruta para la página de selección de reportes."""
    return render_template("reports.html")

def generar_charts(activos: list[dict]) -> str:
    """
    Genera un gráfico de barras del valor promedio de los activos.
    Guarda el gráfico como PNG y devuelve su ruta estática.
    """
    if not activos:
        print("[INFO] No hay activos para generar el gráfico de valores.")
        return ""

    nombres = [a["nombre"] for a in activos]
    valores = [(a["confidencialidad"] + a["integridad"] + a["disponibilidad"]) / 3
               for a in activos]

    plt.figure(figsize=(10, 6))
    plt.bar(nombres, valores, color='skyblue')
    plt.xlabel("Nombre del Activo")
    plt.ylabel("Valor Promedio (C+I+D)/3")
    plt.title("Valor Promedio de Activos por Criterio (Confidencialidad, Integridad, Disponibilidad)")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(np.arange(0, 6, 1))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    path = os.path.join(chart_output_path, "asset_values.png")
    plt.savefig(path)
    plt.close()

    return f"/static/{CHART_DIR_NAME}/asset_values.png"

def generar_matriz(riesgos: list[dict]) -> str:
    """
    Genera una matriz de riesgo global.
    Guarda la matriz como PNG y devuelve su ruta estática.
    """
    if not riesgos:
        print("[INFO] No hay riesgos para generar la matriz de riesgo.")
        return ""

    mat = np.zeros((5, 5), dtype=int)
    for r in riesgos:
        try:
            p = max(0, min(4, int(r.get("probabilidad", 1)) - 1))
            i = max(0, min(4, int(r.get("impacto", 1)) - 1))
            mat[4 - i, p] += 1
        except (ValueError, TypeError):
            print(f"[WARNING] Datos de riesgo inválidos para cálculo de matriz: {r}")
            continue

    masked = np.ma.masked_equal(mat, 0)
    fig, ax = plt.subplots(figsize=(7,7))
    ax.set_facecolor("#f0f0f0")
    im = ax.imshow(masked, origin="lower", interpolation="none",
                    cmap="Reds", vmin=1, vmax=mat.max() if mat.max() > 0 else 1)
    fig.colorbar(im, ax=ax, shrink=0.7, label="# Riesgos")
    ax.set_xticks(np.arange(-.5, 5, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 5, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.5)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_xticks(range(5)); ax.set_yticks(range(5))
    ax.set_xticklabels([1,2,3,4,5]); ax.set_yticklabels(list(reversed([1,2,3,4,5])))
    ax.set_xlabel("Probabilidad"); ax.set_ylabel("Impacto")
    ax.set_title("Matriz de Riesgo Global")
    for (row, col), val in np.ndenumerate(mat):
        if val > 0:
            ax.text(col, row, str(val), ha="center", va="center",
                    color="black", fontweight="bold", fontsize=10)
    plt.tight_layout()

    path = os.path.join(chart_output_path, "risk_matrix.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)

    return f"/static/{CHART_DIR_NAME}/risk_matrix.png"

@app.route("/reports/view")
def report_view():
    """
    Muestra una vista previa de los gráficos de activos y riesgos.
    Los gráficos se generan bajo demanda.
    """
    activos = lista_activos()
    riesgos = lista_riesgos()

    chart_asset_path = generar_charts(activos)
    chart_matrix_path = generar_matriz(riesgos)

    report_date = datetime.now().strftime("%Y-%m-%d")
    report_author = "Usuario del Sistema" # O del usuario autenticado

    return render_template(
        "report.html",
        fecha=report_date,
        autor=report_author,
        activos=activos,
        riesgos=riesgos,
        chart_asset=chart_asset_path,
        chart_matrix=chart_matrix_path,
    )

@app.route("/reports/download")
def report_download():
    """
    Descarga el informe PDF generado por el microservicio de reportes.
    Esta ruta llama al microservicio de reportes para obtener el PDF.
    """
    activos = lista_activos()
    riesgos = lista_riesgos()

    report_date = datetime.now().strftime("%Y-%m-%d")
    report_author = "Usuario del Sistema" # O del usuario autenticado

    try:
        # Llamar al microservicio de reportes para generar el PDF
        response = requests.post(
            REPORT_MICROSERVICE_URL,
            data={
                "activos": json.dumps(activos),
                "riesgos": json.dumps(riesgos),
                "fecha": report_date,
                "autor": report_author,
            },
            timeout=15 # Timeout para la petición HTTP
        )
        response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)

        if response.content and len(response.content) > 1000: # Mínimo tamaño para un PDF válido
            temp_pdf_filename = f"informe_ciber_riesgos_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            temp_pdf_path = os.path.join(report_output_path, temp_pdf_filename)

            with open(temp_pdf_path, "wb") as f:
                f.write(response.content)

            # Devolver el archivo como descarga
            flask_response = send_file(temp_pdf_path, as_attachment=True, download_name="informe_ciber_riesgos.pdf", mimetype="application/pdf")

            # Limpiar el archivo temporal después de enviarlo
            @flask_response.call_on_close
            def cleanup():
                try:
                    os.remove(temp_pdf_path)
                    print(f"Archivo temporal {temp_pdf_path} eliminado.")
                except Exception as e:
                    print(f"Error al eliminar archivo temporal {temp_pdf_path}: {e}")
            return flask_response
        else:
            return "Error: El microservicio de reportes no está disponible o la respuesta no es válida.", 503

    except requests.exceptions.Timeout:
        return f"Error: Tiempo de espera agotado al contactar al microservicio de reportes en {REPORT_MICROSERVICE_URL}", 503
    except requests.exceptions.ConnectionError:
        return f"Error: No se pudo conectar al microservicio de reportes en {REPORT_MICROSERVICE_URL}. Asegúrate de que Kong y el microservicio estén corriendo.", 503
    except requests.exceptions.HTTPError as e:
        return f"Error HTTP del microservicio de reportes ({e.response.status_code}): {e.response.text}", 503
    except Exception as e:
        print(f"Error inesperado en report_download: {e}")
        return "Error interno del servidor al procesar la descarga del informe.", 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
