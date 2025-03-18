from flask import Flask
from flask_cors import CORS
from app.api import api_bp
from app.auth import auth_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 