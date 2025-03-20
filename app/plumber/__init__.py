from flask import Blueprint

bp = Blueprint('plumber', __name__)

from app.plumber import routes 