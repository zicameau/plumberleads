from flask import Flask
from flask_cors import CORS

def init_app():
    """Initialize the core application."""
    app = Flask(__name__)
    CORS(app)
    
    return app 