#!/usr/bin/env python
"""
Run script for PlumberLeads application.
This is a convenience script for running the application during development.
"""
import os
from app import create_app
from config import DevelopmentConfig, TestingConfig, ProductionConfig

# Get the environment from FLASK_ENV or default to 'development'
env = os.environ.get('FLASK_ENV', 'development')

# Map environment names to config classes
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

# Get the appropriate config class
config_class = config_map.get(env, DevelopmentConfig)

# Create the application with the selected config
app = create_app(config_class)

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = env != 'production'
    
    print(f"Starting PlumberLeads in {env} mode...")
    app.run(host=host, port=port, debug=debug) 