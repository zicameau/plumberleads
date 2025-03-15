#!/usr/bin/env python
"""
Database initialization script.
Run this script to create all database tables before starting the application.
"""
import os
import sys
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_db():
    """Initialize the database with all required tables."""
    # Create a minimal Flask app
    app = Flask(__name__)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI') or os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Import models and initialize SQLAlchemy
    from app.models.base import db, Base, User, Plumber, Lead, LeadClaim, Setting
    db.init_app(app)
    
    # Create tables within app context
    with app.app_context():
        try:
            print("Creating database tables...")
            Base.metadata.create_all(db.engine)
            print("Database tables created successfully!")
            
            # List all tables that were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables in database: {', '.join(tables)}")
            
            # Check if users table exists
            if 'users' in tables:
                print("Users table exists!")
                # Check if admin user exists
                admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
                admin_user = db.session.query(User).filter_by(email=admin_email).first()
                if admin_user:
                    print(f"Admin user {admin_email} exists!")
                else:
                    print(f"Admin user {admin_email} does not exist.")
            else:
                print("Users table does not exist!")
            
            return True
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")
            return False

if __name__ == "__main__":
    print("Initializing database...")
    success = init_db()
    if success:
        print("Database initialization completed successfully!")
    else:
        print("Database initialization failed!")
        sys.exit(1) 