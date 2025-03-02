# run.py
import os
from app import create_app
from flask.cli import FlaskGroup

app = create_app()

def main():
    """Main entry point for the application."""
    app.run(host='0.0.0.0', debug=True)

if __name__ == '__main__':
    main()
