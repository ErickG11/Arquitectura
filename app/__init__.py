from flask import Flask
from .routes import register_routes
from .config import configure_environment
from modules.db import Base, engine
import modules.catalog.models
import modules.assets.models
import modules.risks.models

def create_app():
    app = Flask(__name__)
    configure_environment(app)
    register_routes(app)
    Base.metadata.create_all(bind=engine)
    return app
