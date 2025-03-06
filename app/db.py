import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from contextlib import contextmanager

# Get the database logger
logger = logging.getLogger('database')

class Database:
    """Database connection manager."""
    
    def __init__(self, app=None):
        self.app = app
        self._connection = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app."""
        self.app = app
        
        # Close connection when app context ends
        app.teardown_appcontext(self.close_connection)
    
    @property
    def connection(self):
        """Get database connection, creating it if needed."""
        if self._connection is None:
            try:
                logger.info("Creating new database connection")
                
                # Get connection parameters from environment or config
                db_url = os.environ.get('DATABASE_URL')
                
                if db_url:
                    # Heroku-style connection string
                    self._connection = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
                else:
                    # Individual connection parameters
                    self._connection = psycopg2.connect(
                        host=os.environ.get('DB_HOST', 'localhost'),
                        port=os.environ.get('DB_PORT', '5432'),
                        database=os.environ.get('DB_NAME', 'plumber_leads'),
                        user=os.environ.get('DB_USER', 'postgres'),
                        password=os.environ.get('DB_PASSWORD', ''),
                        cursor_factory=RealDictCursor
                    )
                
                # Enable autocommit mode
                self._connection.autocommit = True
                
                logger.info("Database connection established")
            except Exception as e:
                logger.error(f"Database connection error: {str(e)}", exc_info=True)
                raise
        
        return self._connection
    
    def close_connection(self, exception=None):
        """Close the database connection."""
        if self._connection is not None:
            logger.info("Closing database connection")
            self._connection.close()
            self._connection = None
    
    def execute(self, query, params=None):
        """Execute a SQL query and return the cursor."""
        try:
            cursor = self.connection.cursor()
            
            # Log query (sanitize sensitive data)
            log_query = query
            if params and any(k for k in params.keys() if 'password' in k.lower()):
                # Create a copy of params with password values masked
                log_params = {k: '******' if 'password' in k.lower() else v for k, v in params.items()}
                logger.debug(f"Executing query with params: {log_params}")
            else:
                logger.debug(f"Executing query with params: {params}")
            
            cursor.execute(query, params or {})
            return cursor
        except Exception as e:
            logger.error(f"Database query error: {str(e)}\nQuery: {query}\nParams: {params}", exc_info=True)
            raise
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        connection = self.connection
        
        try:
            logger.info("Starting database transaction")
            # Turn off autocommit for transaction
            old_autocommit = connection.autocommit
            connection.autocommit = False
            
            yield connection
            
            # Commit the transaction
            connection.commit()
            logger.info("Transaction committed")
        except Exception as e:
            # Rollback on error
            connection.rollback()
            logger.error(f"Transaction rolled back due to error: {str(e)}", exc_info=True)
            raise
        finally:
            # Restore previous autocommit setting
            connection.autocommit = old_autocommit

# Create a global instance
db = Database() 