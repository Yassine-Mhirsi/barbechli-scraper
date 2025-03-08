import logging
import threading
import os
from scraper import (
    get_product_ids, 
    get_product_details, 
    save_results, 
    save_to_products_file,
    save_to_database,
    all_products, 
    producer_done, 
    product_queue
)

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    logging.info("Starting scraping process")
    #category = "fashion_beauty"
    text = "ordinateur%20portable"  
    sources = "cyberinfo"
    subcategories = "laptops"
    
    # Use a single products.json file for all stores and categories
    output_file = "output/products.json"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    logging.info(f"Output will be saved to: {output_file}")

    NUM_CONSUMERS = 5  # Number of concurrent consumer threads
    
    # Create threads
    producer_thread = threading.Thread(target=get_product_ids, args=(text,subcategories,sources))
    consumer_threads = [threading.Thread(target=get_product_details) for _ in range(NUM_CONSUMERS)]
    saver_thread = threading.Thread(target=save_results, args=(output_file,))
    
    # Start all threads
    producer_thread.start()
    for consumer_thread in consumer_threads:
        consumer_thread.start()
    saver_thread.start()
    
    # Wait for all threads to complete
    producer_thread.join()
    for consumer_thread in consumer_threads:
        consumer_thread.join()
    saver_thread.join()
    
    # Final save to JSON file
    save_to_products_file(all_products, output_file)
    
    # Save to PostgreSQL database
    logging.info("Saving products to PostgreSQL database...")
    db_stats = save_to_database(all_products)
    if db_stats:
        logging.info(f"Database save completed. Total products in database: {db_stats['total_products']}")
    
    logging.info(f"Scraping completed. Saved products to {output_file} and database")