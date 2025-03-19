from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import leads, plumbers, payments, admin 