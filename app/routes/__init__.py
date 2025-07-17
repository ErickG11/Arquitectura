from modules.assets.routes import assets_bp
from modules.risks.routes import risks_bp
from .home import home_bp
from .report import report_bp

def register_routes(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(report_bp, url_prefix="/reports")
    app.register_blueprint(assets_bp, url_prefix="/assets")
    app.register_blueprint(risks_bp, url_prefix="/risks")
    app.url_map.strict_slashes = False
