import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# --- Database and extensions ---
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# This tells Flask-Login which route handles logging in
login_manager.login_view = 'main.login'
# This is the message it will flash
login_manager.login_message = 'Please log in to access this page.'

def create_app(config_class=Config):
    """
    The application factory. Creates and configures the Flask app.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # --- Initialize extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # --- NEW CODE TO CREATE UPLOAD FOLDER ---
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Already exists

    # Ensure the upload folder exists
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass # Already exists
    # --- END OF NEW CODE ---

    # --- Register Blueprints ---
    # We import 'bp' (our Blueprint) from app.routes here
    # to avoid circular imports.
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    # --- Database context ---
    # This ensures that when the app is created,
    # it knows about the database models.
    from app import models

    return app

