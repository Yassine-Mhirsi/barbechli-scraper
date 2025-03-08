from playwright.sync_api import sync_playwright
import json
import os
from typing import List, Optional, Dict
import logging
import queue
import threading
import time
import db

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
                    page.wait_for_timeout(3000)
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

            if response_body and "response" in response_body and len(response_body["response"]) > 0:
                # Extract the product data and clean it up
                product_data = response_body["response"][0]
                
                # Create a cleaned product object with only the fields we want
                cleaned_product = {
                    "uniqueID": product_data.get("uniqueID", ""),
                    "title": product_data.get("title", ""),
                    "store_label": product_data.get("store_label", ""),
                    "category": product_data.get("category", ""),
                    "subcategory": product_data.get("subcategory", ""),
                    "source_name": product_data.get("source_name", ""),
                    "image": product_data.get("image", ""),
                    "currency": product_data.get("currency", ""),
                    "price": product_data.get("price", 0),
                    "price_min": product_data.get("price_min", 0),
                    "price_max": product_data.get("price_max", 0),
                    "price_drop": product_data.get("price_drop", 0),
                    "price_drop_percent": product_data.get("price_drop_percent", 0),
                    "price_week_changed": product_data.get("price_week_changed", ""),
                    "price_week_drop": product_data.get("price_week_drop", 0),
                    "price_week_drop_percent": product_data.get("price_week_drop_percent", 0),
                    "price_deal": product_data.get("price_deal", ""),
                    "price_hot_deal": product_data.get("price_hot_deal", ""),
                    "price_top_deal": product_data.get("price_top_deal", ""),
                    "link": product_data.get("link", ""),
                    "source_link": product_data.get("source_link", ""),
                    "brand": product_data.get("brand", ""),
                    "availability": product_data.get("availability", ""),
                    "clicks": product_data.get("clicks", 0),
                    "clicksExternal": product_data.get("clicksExternal", 0),
                    "priceTable": product_data.get("priceTable", []),
                    "availabilityTable": product_data.get("availabilityTable", []),
                    "date_creation": product_data.get("date_creation", "")
                }
                
                with products_lock:
                    all_products.append(cleaned_product)
                logging.info(f"Successfully processed product {product_id}")
            else:
                logging.warning(f"No response body received for product {product_id}")

        context.close()
        browser.close()

def save_results(output_file='products.json'):
    """
    Save results to a single products.json file without overwriting existing data.
    """
    while not (producer_done.is_set() and product_queue.empty()):
        time.sleep(2)
        # Save current progress
        with products_lock:
            save_to_products_file(all_products, output_file)
            logging.info(f"Saved {len(all_products)} products to {output_file}")

def save_to_products_file(new_products, output_file='products.json'):
    """
    Save products to a single JSON file without overwriting existing data.
    Also generates and includes statistics about the products.
    
    Args:
        new_products: List of new products to add
        output_file: Output file name (default: products.json)
    """
    # Create products structure if it doesn't exist
    products_data = {"stats": {}, "products": []}
    
    # Load existing data if file exists
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
                if "products" not in products_data:
                    products_data["products"] = []
                if "stats" not in products_data:
                    products_data["stats"] = {}
        except json.JSONDecodeError:
            logging.error(f"Error reading {output_file}, creating new file")
    
    # Get existing product IDs to avoid duplicates
    existing_ids = {product.get("uniqueID") for product in products_data.get("products", [])}
    
    # Add new products that don't already exist
    for product in new_products:
        if product.get("uniqueID") not in existing_ids:
            products_data["products"].append(product)
            existing_ids.add(product.get("uniqueID"))
    
    # Generate statistics
    all_products = products_data["products"]
    
    # Count total products
    total_products = len(all_products)
    
    # Count products by source
    sources_count = {}
    for product in all_products:
        source_name = product.get("source_name")
        if source_name:
            sources_count[source_name] = sources_count.get(source_name, 0) + 1
    
    # Calculate percentages and create source stats
    sources_stats = []
    for source_name, count in sources_count.items():
        percentage = round((count / total_products) * 100, 2) if total_products > 0 else 0
        sources_stats.append({
            "name": source_name,
            "products": count,
            "percentage": percentage
        })
    
    # Sort sources by product count (descending)
    sources_stats.sort(key=lambda x: x["products"], reverse=True)
    
    # Update stats in the data structure
    products_data["stats"] = {
        "total_products": total_products,
        "total_sources": len(sources_count),
        "sources": sources_stats
    }
    
    # Save the updated data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products_data, f, indent=2, ensure_ascii=False)

def save_to_database(products):
    """
    Save products to the PostgreSQL database.
    
    Args:
        products: List of product dictionaries
    """
    try:
        # Create tables if they don't exist
        db.create_tables()
        
        # Insert products into the database
        db.insert_products(products)
        
        # Get updated stats
        stats = db.get_product_stats()
        logging.info(f"Database stats: {stats['total_products']} total products from {stats['total_sources']} sources")
        
        return stats
    except Exception as e:
        logging.error(f"Error saving to database: {e}")
        return None