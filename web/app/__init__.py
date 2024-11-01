# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os
from config import Config

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Using configuration from config.py

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)

    # Ensure the 'uploads' folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Register blueprints to avoid import loops
    from app.routes.frontend import frontend_bp
    from app.routes.upload import upload_bp
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.callback import callback_bp

    app.register_blueprint(frontend_bp)
    app.register_blueprint(callback_bp, url_prefix='/api/callback')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')

    return app