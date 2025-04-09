from flask import Flask
from app.config import Config
from app.views.main_views import main_bp
from app.views.admin_views import admin_bp
from app.models.database import init_db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar base de datos con contexto
    with app.app_context():
        init_db(app)
    
    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    @app.after_request
    def add_header(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response
    
    return app