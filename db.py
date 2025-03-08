import os
import logging
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database connection string from environment variables
DB_URI = os.getenv('POSTGRESQL_URI')

def get_connection():
    """
    Create and return a connection to the PostgreSQL database.
    """
    try:
        conn = psycopg2.connect(DB_URI)
        return conn
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        raise

def create_tables():
    """
    Create the necessary tables in the database if they don't exist.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create products table with lowercase column names
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                uniqueid VARCHAR(255) PRIMARY KEY,
                title TEXT,
                store_label TEXT,
                category TEXT,
                subcategory TEXT,
                source_name TEXT,
                image TEXT,
                currency TEXT,
                price FLOAT,
                price_min FLOAT,
                price_max FLOAT,
                price_drop FLOAT,
                price_drop_percent FLOAT,
                price_week_changed TEXT,
                price_week_drop FLOAT,
                price_week_drop_percent FLOAT,
                price_deal BOOLEAN,
                price_hot_deal BOOLEAN,
                price_top_deal BOOLEAN,
                link TEXT,
                source_link TEXT,
                brand TEXT,
                availability TEXT,
                clicks INTEGER,
                clicksexternal INTEGER,
                date_creation TIMESTAMP,
                date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create price_history table for storing price changes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id SERIAL PRIMARY KEY,
                product_id VARCHAR(255) REFERENCES products(uniqueid),
                price FLOAT,
                date TIMESTAMP,
                UNIQUE(product_id, date)
            )
        """)
        
        # Create availability_history table for storing availability changes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS availability_history (
                id SERIAL PRIMARY KEY,
                product_id VARCHAR(255) REFERENCES products(uniqueid),
                availability TEXT,
                date TIMESTAMP,
                UNIQUE(product_id, date)
            )
        """)
        
        conn.commit()
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def insert_products(products):
    """
    Insert or update products in the database.
    
    Args:
        products: List of product dictionaries
    """
    if not products:
        logging.info("No products to insert")
        return
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Prepare data for insertion with lowercase column names
        columns = [
            'uniqueid', 'title', 'store_label', 'category', 'subcategory', 
            'source_name', 'image', 'currency', 'price', 'price_min', 
            'price_max', 'price_drop', 'price_drop_percent', 'price_week_changed',
            'price_week_drop', 'price_week_drop_percent', 'price_deal', 
            'price_hot_deal', 'price_top_deal', 'link', 'source_link', 
            'brand', 'availability', 'clicks', 'clicksexternal', 'date_creation'
        ]
        
        # Map from original keys to lowercase keys
        key_mapping = {
            'uniqueID': 'uniqueid',
            'clicksExternal': 'clicksexternal'
        }
        
        # Convert boolean strings to actual booleans
        for product in products:
            for field in ['price_deal', 'price_hot_deal', 'price_top_deal']:
                if field in product and isinstance(product[field], str):
                    product[field] = product[field].lower() == 'true'
        
        # Create values list for each product
        values = []
        for product in products:
            product_values = []
            for col_original in ['uniqueID', 'title', 'store_label', 'category', 'subcategory', 
                      'source_name', 'image', 'currency', 'price', 'price_min', 
                      'price_max', 'price_drop', 'price_drop_percent', 'price_week_changed',
                      'price_week_drop', 'price_week_drop_percent', 'price_deal', 
                      'price_hot_deal', 'price_top_deal', 'link', 'source_link', 
                      'brand', 'availability', 'clicks', 'clicksExternal', 'date_creation']:
                # Get the lowercase column name
                col = key_mapping.get(col_original, col_original.lower())
                # Get the value using the original key
                product_values.append(product.get(col_original, None))
            values.append(tuple(product_values))
        
        # Create the ON CONFLICT clause for updating existing products
        update_cols = [col for col in columns if col != 'uniqueid']
        update_clause = sql.SQL(', ').join(
            sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(col), sql.Identifier(col))
            for col in update_cols
        )
        
        # Build and execute the query
        query = sql.SQL("""
            INSERT INTO products ({})
            VALUES %s
            ON CONFLICT (uniqueid) DO UPDATE SET
                {},
                date_updated = CURRENT_TIMESTAMP
        """).format(
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            update_clause
        )
        
        execute_values(cursor, query, values)
        
        # Insert price and availability history
        for product in products:
            product_id = product.get('uniqueID')
            price = product.get('price')
            availability = product.get('availability')
            
            # Insert price history
            if price is not None:
                cursor.execute("""
                    INSERT INTO price_history (product_id, price, date)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (product_id, date) DO UPDATE SET price = EXCLUDED.price
                """, (product_id, price))
            
            # Insert availability history
            if availability:
                cursor.execute("""
                    INSERT INTO availability_history (product_id, availability, date)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (product_id, date) DO UPDATE SET availability = EXCLUDED.availability
                """, (product_id, availability))
            
            # Insert price table history if available
            price_table = product.get('priceTable', [])
            for price_entry in price_table:
                if isinstance(price_entry, dict) and 'date' in price_entry and 'price' in price_entry:
                    try:
                        cursor.execute("""
                            INSERT INTO price_history (product_id, price, date)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (product_id, date) DO NOTHING
                        """, (product_id, price_entry['price'], price_entry['date']))
                    except Exception as e:
                        logging.warning(f"Error inserting price history for {product_id}: {e}")
            
            # Insert availability table history if available
            availability_table = product.get('availabilityTable', [])
            for avail_entry in availability_table:
                if isinstance(avail_entry, dict) and 'date' in avail_entry and 'availability' in avail_entry:
                    try:
                        cursor.execute("""
                            INSERT INTO availability_history (product_id, availability, date)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (product_id, date) DO NOTHING
                        """, (product_id, avail_entry['availability'], avail_entry['date']))
                    except Exception as e:
                        logging.warning(f"Error inserting availability history for {product_id}: {e}")
        
        conn.commit()
        logging.info(f"Successfully inserted/updated {len(products)} products in the database")
    except Exception as e:
        logging.error(f"Error inserting products: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def get_product_stats():
    """
    Get statistics about products in the database.
    
    Returns:
        dict: Statistics about products
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get total products count
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        
        # Get count by source
        cursor.execute("""
            SELECT source_name, COUNT(*) as count
            FROM products
            WHERE source_name IS NOT NULL
            GROUP BY source_name
            ORDER BY count DESC
        """)
        sources = cursor.fetchall()
        
        # Format sources data
        sources_stats = []
        for source_name, count in sources:
            percentage = round((count / total_products) * 100, 2) if total_products > 0 else 0
            sources_stats.append({
                "name": source_name,
                "products": count,
                "percentage": percentage
            })
        
        return {
            "total_products": total_products,
            "total_sources": len(sources),
            "sources": sources_stats
        }
    except Exception as e:
        logging.error(f"Error getting product stats: {e}")
        return {
            "total_products": 0,
            "total_sources": 0,
            "sources": []
        }
    finally:
        if conn:
            conn.close() 