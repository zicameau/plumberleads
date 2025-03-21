#!/usr/bin/env python
"""
Reset database script for PlumberLeads application.
This script drops all tables and recreates them.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def reset_database():
    """Reset the application database"""
    print("Starting database reset...")
    
    try:
        from app import create_app, db
        from app.models import User, Lead, Payment, LeadHistory
        from sqlalchemy import text

        app = create_app()
        
        with app.app_context():
            print("Dropping all tables...")
            db.drop_all()
            
            print("Creating all tables...")
            db.create_all()
            
            # Only install PostgreSQL extensions if using PostgreSQL
            if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql'):
                print("Installing required PostgreSQL extensions...")
                with db.engine.connect() as conn:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS cube"))
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS earthdistance"))
                    conn.commit()
            else:
                print("Skipping PostgreSQL extensions (not using PostgreSQL)")
            
            print("Database reset successfully!")
            
            # Optional: Initialize with sample data
            create_sample_data = input("Do you want to create sample data? (y/n): ").lower().strip() == 'y'
            if create_sample_data:
                try:
                    from init_db import initialize_database
                    initialize_database(app)
                    print("Sample data created successfully!")
                except Exception as e:
                    print(f"Error creating sample data: {e}")
    
    except Exception as e:
        print(f"Error resetting database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    confirm = input("This will PERMANENTLY DELETE all data in the database. Are you sure? (type 'yes' to confirm): ")
    
    if confirm.lower() != 'yes':
        print("Operation cancelled.")
        sys.exit(0)
    
    success = reset_database()
    
    if success:
        print("Database reset complete.")
    else:
        print("Database reset failed.")
        sys.exit(1) 