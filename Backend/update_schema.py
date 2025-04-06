from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upgrade_database():
    """
    Upgrade the database schema by adding missing columns.
    This is a simple migration script to add role column to users table.
    """
    logger.info("Starting database schema upgrade...")
    
    # Get database URL from environment
    DATABASE_URL = os.environ.get("DATABASE_URL")
    
    if not DATABASE_URL:
        logger.error("DATABASE_URL not found in environment variables")
        raise ValueError("DATABASE_URL environment variable is not set")
    
    logger.info(f"Using database URL: {DATABASE_URL}")
    
    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    
    try:
        # Check if role column exists in users table
        check_column_query = text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='role'")
        result = conn.execute(check_column_query)
        column_exists = result.fetchone() is not None
        
        if not column_exists:
            logger.info("Adding 'role' column to users table...")
            
            # Add role column with default value 'user'
            add_column_query = text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
            conn.execute(add_column_query)
            
            logger.info("Successfully added 'role' column to users table")
        else:
            logger.info("'role' column already exists in users table")
        
        # Check if updated_at column exists in users table
        check_column_query = text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='updated_at'")
        result = conn.execute(check_column_query)
        column_exists = result.fetchone() is not None
        
        if not column_exists:
            logger.info("Adding 'updated_at' column to users table...")
            
            # Add updated_at column
            add_column_query = text("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            conn.execute(add_column_query)
            
            logger.info("Successfully added 'updated_at' column to users table")
        else:
            logger.info("'updated_at' column already exists in users table")
            
        conn.commit()
        logger.info("Database schema upgrade completed successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error upgrading database schema: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_database() 