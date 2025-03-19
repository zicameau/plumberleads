import os
from app import create_app
from config import config

# Create application instance using the appropriate config
app = create_app(config[os.environ.get('FLASK_ENV', 'default')])

if __name__ == '__main__':
    # Run the application
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=app.config['DEBUG']) 