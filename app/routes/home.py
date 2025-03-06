from flask import Blueprint, render_template, redirect, url_for
import logging

# Get the app logger
logger = logging.getLogger('app')

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    """Home page."""
    logger.info("Home page accessed")
    return render_template('home/index.html') 