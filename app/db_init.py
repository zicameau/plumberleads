"""Database initialization script to ensure all tables exist."""
import os
import sys
from flask import Flask
from app.models.base import Base, db

def create_tables():
    """Create all database tables if they don't exist."""
    # Create a minimal Flask app for database initialization
    app = Flask(__name__)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI') or os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Create tables within app context
    with app.app_context():
        print("Creating database tables...")
        Base.metadata.create_all(db.engine)
        print("Database tables created successfully!")
        
        # List all tables that were created
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables in database: {', '.join(tables)}")
    
    return True

if __name__ == "__main__":
    create_tables() 