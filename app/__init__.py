from flask import Flask
from config import Config
from app.extensions import db  # <--- Importing from the new file

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize plugins
    db.init_app(app)

    # Register Blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app