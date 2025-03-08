import logging
import db

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def test_connection():
    """Test the database connection and create tables."""
    try:
        # Test connection
        conn = db.get_connection()
        logging.info("Successfully connected to the database!")
        conn.close()
        
        # Create tables
        db.create_tables()
        logging.info("Successfully created database tables!")
        
        return True
    except Exception as e:
        logging.error(f"Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    logging.info("Testing database connection...")
    success = test_connection()
    if success:
        logging.info("Database connection test completed successfully!")
    else:
        logging.error("Database connection test failed!") 