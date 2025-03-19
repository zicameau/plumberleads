#!/usr/bin/env python
"""
Run script for PlumberLeads application.
This is a convenience script for running the application during development.
"""
from app import create_app
from config import config
import os

if __name__ == '__main__':
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config[env])
    
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = env != 'production'
    
    print(f"Starting PlumberLeads in {env} mode...")
    app.run(host=host, port=port, debug=debug) 