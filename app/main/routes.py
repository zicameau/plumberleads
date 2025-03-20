from flask import render_template, session

from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    """Home page route."""
    return render_template('index.html') 