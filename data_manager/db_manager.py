import psycopg2
from psycopg2 import pool
from psycopg2.extras import Json, DictCursor
import json
import time
import logging
from datetime import datetime
from config import NEON_URI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_manager/scraper_db.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("db_manager")

# Connection pool for efficient database access
connection_pool = None

def init_db():
    """
    Initialize the database by creating tables if they don't exist
    and setting up a connection pool.
    """
    global connection_pool
    
    try:
        # Create a connection pool with min 1, max 10 connections
        connection_pool = pool.SimpleConnectionPool(1, 10, NEON_URI)
        logger.info("Database connection pool created successfully")
        
        # Get a connection from the pool
        conn = get_connection()
        if not conn:
            logger.error("Failed to get connection from pool")
            return False
        
        # Create tables if they don't exist
        with conn.cursor() as cursor:
            # Create products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    unique_id VARCHAR(255) UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    store_label VARCHAR(255),
                    category VARCHAR(100),
                    subcategory VARCHAR(100),
                    source_name VARCHAR(100),
                    image_url TEXT,
                    currency VARCHAR(10),
                    current_price DECIMAL(10,2),
                    brand VARCHAR(100),
                    availability VARCHAR(50),
                    link TEXT,
                    source_link TEXT,
                    clicks INTEGER DEFAULT 0,
                    clicks_external INTEGER DEFAULT 0,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    additional_data JSONB DEFAULT '{}'::jsonb
                )
            """)
            
            # Create price_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER REFERENCES products(id),
                    price DECIMAL(10,2) NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create availability_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS availability_history (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER REFERENCES products(id),
                    availability VARCHAR(50) NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create source_stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS source_stats (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    products_count INTEGER DEFAULT 0,
                    percentage DECIMAL(5,2) DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_source_name ON products(source_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_product_id ON price_history(product_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_recorded_at ON price_history(recorded_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_availability_history_product_id ON availability_history(product_id)")
            
            conn.commit()
            logger.info("Database tables created successfully")
        
        release_connection(conn)
        return True
    
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False

def get_connection():
    """
    Get a connection from the pool
    """
    global connection_pool
    
    # Try to get a connection, with a few retries in case of temporary issues
    for attempt in range(3):
        try:
            if connection_pool:
                conn = connection_pool.getconn()
                if conn:
                    return conn
            
            logger.warning(f"Connection attempt {attempt+1} failed, retrying...")
            time.sleep(1)  # Wait a bit before retrying
            
        except Exception as e:
            logger.error(f"Error getting connection from pool (attempt {attempt+1}): {e}")
    
    return None

def release_connection(conn):
    """
    Release a connection back to the pool
    """
    global connection_pool
    
    if conn and connection_pool:
        try:
            connection_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error releasing connection to pool: {e}")
            try:
                conn.close()  # Try to close it directly if can't put back in pool
            except:
                pass

def close_all_connections():
    """
    Close all connections in the pool
    """
    global connection_pool
    
    if connection_pool:
        try:
            connection_pool.closeall()
            logger.info("All database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

def add_or_update_product(product_data):
    """
    Add a new product or update an existing one
    
    Args:
        product_data: Dictionary containing product information
        
    Returns:
        Tuple (success, product_id, is_new)
    """
    conn = get_connection()
    if not conn:
        return False, None, False
    
    try:
        with conn.cursor() as cursor:
            # Check if product exists
            cursor.execute(
                "SELECT id, current_price, availability FROM products WHERE unique_id = %s",
                (product_data.get("uniqueID"),)
            )
            result = cursor.fetchone()
            
            # Prepare data for insertion/update
            current_time = datetime.now()
            
            # Extract core fields
            unique_id = product_data.get("uniqueID")
            title = product_data.get("title", "")
            store_label = product_data.get("store_label", "")
            category = product_data.get("category", "")
            subcategory = product_data.get("subcategory", "")
            source_name = product_data.get("source_name", "")
            image_url = product_data.get("image", "")
            currency = product_data.get("currency", "TND")
            current_price = product_data.get("price", 0)
            brand = product_data.get("brand", "")
            availability = product_data.get("availability", "unknown")
            link = product_data.get("link", "")
            source_link = product_data.get("source_link", "")
            clicks = product_data.get("clicks", 0)
            clicks_external = product_data.get("clicksExternal", 0)
            
            # Put remaining fields in additional_data
            additional_data = {k: v for k, v in product_data.items() if k not in [
                "uniqueID", "title", "store_label", "category", "subcategory", 
                "source_name", "image", "currency", "price", "brand", "availability",
                "link", "source_link", "clicks", "clicksExternal", "priceTable",
                "availabilityTable"
            ]}
            
            if result:
                # Product exists, update it
                product_id, old_price, old_availability = result
                
                cursor.execute("""
                    UPDATE products 
                    SET title = %s, store_label = %s, category = %s, subcategory = %s,
                        source_name = %s, image_url = %s, currency = %s, current_price = %s,
                        brand = %s, availability = %s, link = %s, source_link = %s,
                        clicks = %s, clicks_external = %s, last_updated = %s,
                        additional_data = %s
                    WHERE id = %s
                """, (
                    title, store_label, category, subcategory, source_name, image_url,
                    currency, current_price, brand, availability, link, source_link,
                    clicks, clicks_external, current_time, Json(additional_data), product_id
                ))
                
                # Add price history if price has changed
                if old_price != current_price:
                    cursor.execute(
                        "INSERT INTO price_history (product_id, price, recorded_at) VALUES (%s, %s, %s)",
                        (product_id, current_price, current_time)
                    )
                
                # Add availability history if availability has changed
                if old_availability != availability:
                    cursor.execute(
                        "INSERT INTO availability_history (product_id, availability, recorded_at) VALUES (%s, %s, %s)",
                        (product_id, availability, current_time)
                    )
                
                is_new = False
                
            else:
                # Insert new product
                cursor.execute("""
                    INSERT INTO products (
                        unique_id, title, store_label, category, subcategory, source_name,
                        image_url, currency, current_price, brand, availability, link,
                        source_link, clicks, clicks_external, date_creation, last_updated,
                        additional_data
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    unique_id, title, store_label, category, subcategory, source_name,
                    image_url, currency, current_price, brand, availability, link,
                    source_link, clicks, clicks_external, current_time, current_time,
                    Json(additional_data)
                ))
                
                product_id = cursor.fetchone()[0]
                
                # Add initial price history
                cursor.execute(
                    "INSERT INTO price_history (product_id, price, recorded_at) VALUES (%s, %s, %s)",
                    (product_id, current_price, current_time)
                )
                
                # Add initial availability history
                cursor.execute(
                    "INSERT INTO availability_history (product_id, availability, recorded_at) VALUES (%s, %s, %s)",
                    (product_id, availability, current_time)
                )
                
                is_new = True
            
            # Update source stats
            update_source_stats(cursor)
            
            conn.commit()
            logger.info(f"{'Added new' if is_new else 'Updated'} product: {unique_id}")
            return True, product_id, is_new
            
    except Exception as e:
        conn.rollback()
        logger.error(f"Error adding/updating product {product_data.get('uniqueID')}: {e}")
        return False, None, False
    
    finally:
        release_connection(conn)

def update_source_stats(cursor):
    """
    Update source statistics
    
    Args:
        cursor: Database cursor to use for queries
    """
    try:
        # Get total product count
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        
        if total_products == 0:
            return
        
        # Get count by source
        cursor.execute("""
            SELECT source_name, COUNT(*) as count
            FROM products
            WHERE source_name IS NOT NULL AND source_name != ''
            GROUP BY source_name
        """)
        
        source_counts = cursor.fetchall()
        
        # Update stats for each source
        for source_name, count in source_counts:
            percentage = (count / total_products) * 100
            
            cursor.execute("""
                INSERT INTO source_stats (name, products_count, percentage, last_updated)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (name) 
                DO UPDATE SET 
                    products_count = %s,
                    percentage = %s,
                    last_updated = NOW()
            """, (source_name, count, percentage, count, percentage))
            
    except Exception as e:
        logger.error(f"Error updating source stats: {e}")

def get_source_stats():
    """
    Get statistics about product sources
    
    Returns:
        List of dictionaries with source statistics
    """
    conn = get_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT name, products_count, percentage, last_updated
                FROM source_stats
                ORDER BY products_count DESC
            """)
            
            result = cursor.fetchall()
            # Convert to list of dictionaries
            return [dict(row) for row in result]
            
    except Exception as e:
        logger.error(f"Error getting source stats: {e}")
        return []
    
    finally:
        release_connection(conn)

def get_all_products():
    """
    Get all products from the database
    
    Returns:
        List of dictionaries with product data
    """
    conn = get_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT id, unique_id, title, store_label, category, subcategory,
                       source_name, image_url, currency, current_price, brand,
                       availability, link, source_link, clicks, clicks_external,
                       date_creation, last_updated, additional_data
                FROM products
                ORDER BY last_updated DESC
            """)
            
            products = []
            for row in cursor.fetchall():
                product = dict(row)
                
                # Convert additional_data from JSONB to dict
                if 'additional_data' in product and product['additional_data']:
                    # If already a dict, no need to convert
                    if not isinstance(product['additional_data'], dict):
                        product['additional_data'] = dict(product['additional_data'])
                
                # Rename fields to match the expected format
                product['uniqueID'] = product.pop('unique_id')
                product['price'] = product.pop('current_price')
                product['image'] = product.pop('image_url')
                product['clicksExternal'] = product.pop('clicks_external')
                
                # Add price history
                cursor.execute("""
                    SELECT price, recorded_at
                    FROM price_history
                    WHERE product_id = %s
                    ORDER BY recorded_at DESC
                """, (product['id'],))
                
                price_history = cursor.fetchall()
                product['priceTable'] = [
                    {"date_price": str(ph['recorded_at']), "price": float(ph['price'])}
                    for ph in price_history
                ]
                
                # Add availability history
                cursor.execute("""
                    SELECT availability, recorded_at
                    FROM availability_history
                    WHERE product_id = %s
                    ORDER BY recorded_at DESC
                """, (product['id'],))
                
                availability_history = cursor.fetchall()
                product['availabilityTable'] = [
                    {"date_availability": str(ah['recorded_at']), "availability": ah['availability']}
                    for ah in availability_history
                ]
                
                # Convert timestamps to strings
                product['date_creation'] = str(product['date_creation'])
                product['last_updated'] = str(product['last_updated'])
                
                # Merge additional_data fields into the product
                if product['additional_data']:
                    for key, value in product['additional_data'].items():
                        product[key] = value
                    del product['additional_data']
                
                # Remove database ID as it's not needed in the external representation
                del product['id']
                
                products.append(product)
            
            return products
            
    except Exception as e:
        logger.error(f"Error getting all products: {e}")
        return []
    
    finally:
        release_connection(conn)

# Initialize database if this module is run directly
if __name__ == "__main__":
    print("Initializing database...")
    if init_db():
        print("Database initialized successfully")
    else:
        print("Database initialization failed") 