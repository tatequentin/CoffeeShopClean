from flask import Flask
from .routes import bp as main_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'
    app.register_blueprint(main_bp)
    return app
