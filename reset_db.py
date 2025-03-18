#!/usr/bin/env python
# reset_db.py - Reset the database and load fake data

import os
import sys
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("db-reset")

def read_sql_file(filename):
    """Read SQL from a file."""
    with open(filename, 'r') as f:
        return f.read()

def wait_for_postgres(host, port, user, password, dbname, max_retries=30):
    """Wait for Postgres to be available."""
    retries = 0
    while retries < max_retries:
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=dbname
            )
            conn.close()
            logger.info("✅ Postgres is available!")
            return True
        except psycopg2.OperationalError:
            retries += 1
            logger.info(f"Waiting for Postgres to be available... ({retries}/{max_retries})")
            time.sleep(1)
    
    logger.error("❌ Timed out waiting for Postgres")
    return False

def reset_database(conn_params, schema_file):
    """Reset the database using the provided schema."""
    # Extract connection parameters
    host = conn_params.get('host', 'localhost')
    port = conn_params.get('port', 5432)
    user = conn_params.get('user', 'postgres')
    password = conn_params.get('password', 'postgres')
    dbname = conn_params.get('dbname', 'postgres')

    # Wait for Postgres to be ready
    if not wait_for_postgres(host, port, user, password, dbname):
        return False

    try:
        # Connect to the default database
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        logger.info("🗑️ Dropping schemas and tables...")
        
        # Drop the auth schema and public schema objects
        cursor.execute("""
            DROP SCHEMA IF EXISTS auth CASCADE;
            
            DO $$ DECLARE
                r RECORD;
            BEGIN
                -- Drop all tables in public schema
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
                
                -- Drop all types in public schema
                FOR r IN (SELECT typname FROM pg_type 
                          WHERE typtype = 'e' AND typnamespace = 
                          (SELECT oid FROM pg_namespace WHERE nspname = 'public')) LOOP
                    EXECUTE 'DROP TYPE IF EXISTS ' || quote_ident(r.typname) || ' CASCADE';
                END LOOP;
                
                -- Drop all functions in public schema
                FOR r IN (SELECT proname, oid::regprocedure as fullname
                         FROM pg_proc 
                         WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) LOOP
                    EXECUTE 'DROP FUNCTION IF EXISTS ' || r.fullname || ' CASCADE';
                END LOOP;
            END $$;
        """)
        
        # Apply schema
        logger.info("🔄 Applying schema...")
        schema_sql = read_sql_file(schema_file)
        cursor.execute(schema_sql)
        
        # Create extension if not exists
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Database schema reset successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error resetting database: {str(e)}")
        return False

def generate_fake_data():
    """Generate fake data using the utility."""
    try:
        logger.info("🔄 Generating fake data...")
        
        # Add the current directory to the Python path
        sys.path.insert(0, os.getcwd())
        
        # Import the fake_data module and generate data
        from app.utils.fake_data import generate_fake_data
        generate_fake_data()
        
        logger.info("✅ Fake data generated successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Error generating fake data: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Reset database and load fake data")
    parser.add_argument("--schema", default="supabase/migrations/local_schema.sql", 
                      help="Path to schema SQL file")
    parser.add_argument("--no-fake-data", action="store_true",
                      help="Skip generating fake data")
    parser.add_argument("--env-file", default=".env.local",
                      help="Environment file to load database connection info from")
    
    args = parser.parse_args()
    
    # Load environment variables
    db_params = {}
    try:
        from dotenv import load_dotenv
        load_dotenv(args.env_file)
        
        # Parse DATABASE_URL or use individual components
        db_url = os.environ.get('DATABASE_URL')
        if db_url and db_url.startswith('postgresql://'):
            # Extract connection parameters from URL
            import re
            match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)', db_url)
            if match:
                db_params = {
                    'user': match.group(1),
                    'password': match.group(2),
                    'host': match.group(3),
                    'port': int(match.group(4)),
                    'dbname': match.group(5)
                }
        else:
            # Use individual components
            db_params = {
                'host': os.environ.get('DB_HOST', 'localhost'),
                'port': int(os.environ.get('DB_PORT', 5432)),
                'user': os.environ.get('DB_USER', 'postgres'),
                'password': os.environ.get('DB_PASSWORD', 'postgres'),
                'dbname': os.environ.get('DB_NAME', 'postgres')
            }
            
    except Exception as e:
        logger.warning(f"Could not load environment variables: {str(e)}")
        logger.warning("Using default database connection parameters")
    
    # Use default params if none were loaded
    if not db_params:
        db_params = {
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'password': 'postgres',
            'dbname': 'postgres'
        }
    
    logger.info(f"🔄 Resetting database with schema: {args.schema}")
    logger.info(f"📊 Database connection: {db_params['user']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}")
    
    if reset_database(db_params, args.schema):
        if not args.no_fake_data:
            generate_fake_data()
        logger.info("✅ Database reset complete!")
    else:
        logger.error("❌ Database reset failed")
        sys.exit(1)

if __name__ == "__main__":
    main()