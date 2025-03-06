from playwright.sync_api import sync_playwright
import json
from typing import List, Optional
import logging
import queue
import threading
import time

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

# Shared queue for product IDs
product_queue = queue.Queue()
# Event to signal when producer is done
producer_done = threading.Event()
# List to store all products (thread-safe)
all_products = []
# Lock for thread-safe list operations
products_lock = threading.Lock()

def get_product_ids(category: str):
    logging.info(f"Starting to collect product IDs for category: {category}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-extensions',
                '--disable-logging',
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 800, 'height': 600},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            java_script_enabled=True,
        )

        page_number = 1
        has_more_pages = True
        total_products = 0

        while has_more_pages:
            response_data = None
            logging.info(f"Processing page {page_number}")

            def handle_category_request(request):
                if (request.resource_type == "xhr" and 
                    f'https://barbechli.tn/find/?q={{%22category%22:[%22{category}%22],%22key%' in request.url and 
                    f',%22orderby%22:{{%22type%22:%22popularity%22,%22direction%22:%22desc%22,%22desc%22:%22popularity%22}},%22pages%22:{{%22number%22:{page_number},%22rows%22:24}}}}' in request.url):
                    response = request.response()
                    if response:
                        try:
                            nonlocal response_data
                            response_data = json.loads(response.text())
                        except Exception as e:
                            logging.error(f"Error capturing response on page {page_number}: {str(e)}")

            page = context.new_page()
            page.on('request', handle_category_request)

            try:
                url = f"https://barbechli.tn/search;category={category};orderby=popularity;pagenumber={page_number}"
                page.goto(url)
                page.wait_for_timeout(2000)
            except Exception as e:
                logging.error(f"An error occurred: {e}")

            if response_data:
                if "status" in response_data and response_data["status"].get("code") == "ERROR_ELASTIC":
                    logging.info("Reached end of available pages")
                    has_more_pages = False
                else:
                    new_ids = [product["uniqueID"] for product in response_data.get("response", []) if "uniqueID" in product]
                    # Add new IDs to queue
                    for product_id in new_ids:
                        product_queue.put(product_id)
                    total_products += len(new_ids)
                    logging.info(f"Found {len(new_ids)} products on page {page_number}. Total products so far: {total_products}")
                    page_number += 1
            else:
                logging.warning(f"No response data received for page {page_number}")
                has_more_pages = False

            page.close()

        context.close()
        browser.close()
        logging.info(f"Finished collecting product IDs. Total products found: {total_products}")
    
    # Signal that we're done producing IDs
    producer_done.set()

def get_product_details():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-extensions',
                '--disable-logging',
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 800, 'height': 600},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            java_script_enabled=True,
        )

        while not (producer_done.is_set() and product_queue.empty()):
            try:
                # Try to get a product ID from the queue, wait up to 1 second
                product_id = product_queue.get(timeout=1)
            except queue.Empty:
                continue

            logging.info(f"Fetching details for product ID: {product_id}")
            
            page = context.new_page()
            response_body = None

            def handle_request(request):
                if request.resource_type == "xhr" and 'https://barbechli.tn/find/?q={%22uid' in request.url:
                    response = request.response()
                    if response:
                        try:
                            nonlocal response_body
                            response_body = json.loads(response.text())
                            page.close()
                        except Exception as e:
                            logging.error(f"Error capturing response for product {product_id}: {str(e)}")

            page.on('request', handle_request)

            try:
                page.goto(f"https://barbechli.tn/product/{product_id}")
                #page.wait_for_timeout(2000)
            except Exception as e:
                logging.error(f"An error occurred: {e}")

            if response_body:
                with products_lock:
                    all_products.append(response_body)
                logging.info(f"Successfully processed product {product_id}")
            else:
                logging.warning(f"No response body received for product {product_id}")

        context.close()
        browser.close()

def save_results():
    while not (producer_done.is_set() and product_queue.empty()):
        time.sleep(2)
        # Save current progress
        with products_lock:
            with open('all_products.json', 'w', encoding='utf-8') as f:
                json.dump(all_products, f, indent=2, ensure_ascii=False)
            logging.info(f"Saved {len(all_products)} products to all_products.json")

if __name__ == "__main__":
    logging.info("Starting scraping process")
    category = "fashion_beauty"
    NUM_CONSUMERS = 2  # Number of concurrent consumer threads
    
    # Create threads
    producer_thread = threading.Thread(target=get_product_ids, args=(category,))
    consumer_threads = [threading.Thread(target=get_product_details) for _ in range(NUM_CONSUMERS)]
    saver_thread = threading.Thread(target=save_results)
    
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
    
    # Final save
    with open('all_products.json', 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    
    logging.info(f"Scraping completed. Saved {len(all_products)} products to all_products.json")