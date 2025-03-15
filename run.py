#!/usr/bin/env python
"""
Application runner script with database initialization.
"""
import os
import sys
from app import create_app
from app.models.base import db, Base

# Create the Flask app at module level for Gunicorn
app = create_app(os.getenv('FLASK_ENV', 'development'))

# Initialize the database
with app.app_context():
    try:
        print("Checking database tables...")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'users' not in tables:
            print("Creating database tables...")
            Base.metadata.create_all(db.engine)
            print("Database tables created successfully!")
            
            # List all tables that were created
            tables = inspector.get_table_names()
            print(f"Tables in database: {', '.join(tables)}")
        else:
            print("Database tables already exist.")
    except Exception as e:
        print(f"Error checking/creating database tables: {str(e)}")

def main():
    """Run the application."""
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
