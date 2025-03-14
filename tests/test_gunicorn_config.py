import multiprocessing
import pytest
from gunicorn.app.base import BaseApplication
from gunicorn.config import Config
from gunicorn.workers.sync import SyncWorker

def test_gunicorn_config():
    """Test Gunicorn configuration"""
    config = Config()
    
    # Test basic configuration
    assert config.worker_class == SyncWorker
    assert config.workers == 1  # Default is 1, not based on CPU count
    assert config.threads == 1
    
    # Test timeouts
    assert config.timeout == 30
    assert config.graceful_timeout == 30
    assert config.keepalive == 2

    # Test logging
    assert config.accesslog == '-'
    assert config.errorlog == '-'
    assert config.loglevel == 'info'

def test_wsgi_application():
    """Test WSGI application loading"""
    from app import create_app
    app = create_app('testing')
    assert callable(app.wsgi_app) 