# Import all configuration classes for easy access
try:
    from app.config.development import DevelopmentConfig
except ImportError:
    pass

try:
    from app.config.production import ProductionConfig
except ImportError:
    pass

try:
    from app.config.local import LocalConfig
except ImportError:
    pass

try:
    from app.config.testing import TestingConfig
except ImportError:
    pass

__all__ = ['DevelopmentConfig', 'ProductionConfig', 'LocalConfig'] 