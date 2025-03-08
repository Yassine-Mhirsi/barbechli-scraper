from playwright.sync_api import sync_playwright
import json
from typing import List, Optional
import logging
import queue
import threading
import time
import requests

import requests
import logging

import requests
import logging
from typing import List, Dict, Any

def save_to_api():
    """
    Continuously sends product data to the FastAPI /products endpoint.
    """
    while not (producer_done.is_set() and product_queue.empty()):
        with products_lock:  # Use a lock for thread-safe access
            if all_products:
                product = all_products.pop(0)  # Get the first product
                try:
                    # Prepare the product data
                    product = {
                        "uniqueID": product.get("uniqueID"),
                        "title": product.get("title"),
                        "summary": product.get("summary"),
                        "currency": product.get("currency"),
                        "price": float(product.get("price")),
                        "price_min": float(product.get("price_min")),
                        "price_max": float(product.get("price_max")),
                        "price_drop": float(product.get("price_drop")),
                        "price_drop_percent": float(product.get("price_drop_percent")),
                        "price_week_changed": product.get("price_week_changed"),
                        "price_week_drop": float(product.get("price_week_drop")),
                        "price_week_drop_percent": float(product.get("price_week_drop_percent")),
                        "price_deal": product.get("price_deal"),
                        "price_hot_deal": product.get("price_hot_deal"),
                        "price_top_deal": product.get("price_top_deal"),
                        "link": product.get("link"),
                        "category": product.get("category"),
                        "subcategory": product.get("subcategory"),
                        "source_name": product.get("source_name"),
                        "source_link": product.get("source_link"),
                        "brand": product.get("brand"),
                        "model": product.get("model"),
                        "gender": product.get("gender"),
                        "color": product.get("color"),
                        "material": product.get("material"),
                        "store": product.get("store"),
                        "store_label": product.get("store_label"),
                        "store_description": product.get("store_description"),
                        "delivery": product.get("delivery"),
                        "delivery_description": product.get("delivery_description"),
                        "availability": product.get("availability"),
                        "clicks": int(product.get("clicks")),
                        "clicksExternal": int(product.get("clicksExternal")),
                        "reviewsNumber": int(product.get("reviewsNumber")),
                        "reviewsValue": float(product.get("reviewsValue")),
                        "priceTable": [
                            {
                                "date_price": entry.get("date_price"),
                                "price": float(entry.get("price"))
                            }
                            for entry in product.get("priceTable", [])
                        ],
                        "availabilityTable": [
                            {
                                "date_availability": entry.get("date_availability"),
                                "availability": entry.get("availability")
                            }
                            for entry in product.get("availabilityTable", [])
                        ],
                        "image": product.get("image"),
                        "date_creation": product.get("date_creation"),
                        "imageSearch": product.get("imageSearch")
                    }
        
                    # Send data to FastAPI endpoint
                    response = requests.post(
                        "http://127.0.0.1:8000/products",  # FastAPI endpoint
                        json=product,  # Send data as JSON
                        headers={"Content-Type": "application/json"}  # Set content type
                    )
                    
                    # Check if the request was successful
                    if response.status_code == 200:
                        logging.info(f"Inserted product: {product['title']}")
                    else:
                        logging.error(f"Failed to insert product: {response.text}")
                except Exception as e:
                    logging.error(f"Error inserting product: {e}")
        time.sleep(1)  # Sleep to avoid busy-waiting

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

def get_product_ids(text: str,subcategories: str,sources: str):
    logging.info(f"Starting to collect product IDs for category: {subcategories}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
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
        MAX_RETRIES = 3

        while has_more_pages:
            response_data = None
            retry_count = 0
            
            while response_data is None and retry_count < MAX_RETRIES:
                if retry_count > 0:
                    logging.warning(f"Retrying page {page_number} (Attempt {retry_count + 1}/{MAX_RETRIES})")
                    time.sleep(2)  # Wait 2 seconds between retries
                else:
                    logging.info(f"Processing page {page_number}")

                def handle_category_request(request):
                    if (request.resource_type == "xhr" and 
                        f'https://barbechli.tn/find/?q={{%22text%22:%22{text}%22,%22key%' in request.url and 
                        #f',%22orderby%22:{{%22type%22:%22popularity%22,%22direction%22:%22desc%22,%22desc%22:%22popularity%22}},%22pages%22:{{%22number%22:{page_number},%22rows%22:24}}}}' in request.url and 
                        f',%22subcategories%22:[%22{subcategories}%22],%22sources%22:[%22{sources}%22],%22orderby%22:{{%22type%22:%22popularity%22,%22direction%22:%22desc%22,%22desc%22:%22popularity%22}},%22pages%22:{{%22number%22:{page_number},%22rows%22:24}}}}' in request.url ):
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
                    url = f"https://barbechli.tn/search;text={text};subcategories={subcategories};sources={sources};orderby=popularity;pagenumber={page_number}"
                    page.goto(url)
                    page.wait_for_timeout(2000)
                except Exception as e:
                    logging.error(f"An error occurred: {e}")

                if not response_data:
                    retry_count += 1
                    if retry_count < MAX_RETRIES:
                        logging.warning(f"No response data received for page {page_number}, will retry")
                    else:
                        logging.error(f"Failed to get response data for page {page_number} after {MAX_RETRIES} attempts")
                        has_more_pages = False

                page.close()

            if response_data:
                if "status" in response_data and response_data["status"].get("code") == "ERROR_ELASTIC":
                    logging.info("Reached end of available pages (ERROR_ELASTIC)")
                    has_more_pages = False
                else:
                    new_ids = [product["uniqueID"] for product in response_data.get("response", []) if "uniqueID" in product]
                    
                    # Check if we got any products
                    if not new_ids:
                        logging.info("Reached end of available pages (no products found)")
                        has_more_pages = False
                    else:
                        # Add new IDs to queue
                        for product_id in new_ids:
                            product_queue.put(product_id)
                        total_products += len(new_ids)
                        logging.info(f"Found {len(new_ids)} products on page {page_number}. Total products so far: {total_products}")
                        
                        # Check if we got fewer products than expected (24 per page)
                        if len(new_ids) < 24:
                            logging.info("Reached end of available pages (last page with fewer products)")
                            has_more_pages = False
                        else:
                            page_number += 1
            else:
                has_more_pages = False

        context.close()
        browser.close()
        logging.info(f"Finished collecting product IDs. Total products found: {total_products}")
    
    # Signal that we're done producing IDs
    producer_done.set()

def get_product_details():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
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

def save_results(output_file='all_products.json'):
    while not (producer_done.is_set() and product_queue.empty()):
        time.sleep(2)
        # Save current progress
        with products_lock:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_products, f, indent=2, ensure_ascii=False)
            logging.info(f"Saved {len(all_products)} products to {output_file}")

if __name__ == "__main__":
    logging.info("Starting scraping process")
    #category = "fashion_beauty"
    text = "mytek"
    sources = "mytek"
    subcategories = "laptops"
    
    # Create dynamic output filename based on store and category
    output_file = f"{sources}_{subcategories}_test.json"
    logging.info(f"Output will be saved to: {output_file}")

    NUM_CONSUMERS = 5  # Number of concurrent consumer threads
    
    # Create threads
    producer_thread = threading.Thread(target=get_product_ids, args=(text,subcategories,sources))
    consumer_threads = [threading.Thread(target=get_product_details) for _ in range(NUM_CONSUMERS)]
    saver_thread = threading.Thread(target=save_results, args=(output_file,))
    api_saver_thread = threading.Thread(target=save_to_api)
    
    # Start all threads
    producer_thread.start()
    for consumer_thread in consumer_threads:
        consumer_thread.start()
    saver_thread.start()
    api_saver_thread.start()
    
    # Wait for all threads to complete
    producer_thread.join()
    for consumer_thread in consumer_threads:
        consumer_thread.join()
    saver_thread.join()
    api_saver_thread.join()
    
    # Final save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    
    logging.info(f"Scraping completed. Saved {len(all_products)} products to {output_file}")