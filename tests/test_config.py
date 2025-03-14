import os
from app import create_app


def test_production_config():
    """Test production configuration"""
    app = create_app('production')
    assert app.config['TESTING'] == False
    assert app.config['DEBUG'] == False
    assert app.config['SQLALCHEMY_DATABASE_URI'] == os.environ.get('DATABASE_URL')

def test_development_config():
    """Test development configuration"""
    app = create_app('development')
    assert app.config['DEBUG'] == True
    assert app.config['TESTING'] == False

def test_testing_config():
    """Test testing configuration"""
    app = create_app('testing')
    assert app.config['TESTING'] == True
    assert app.config['DEBUG'] == True
    assert app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] == False 