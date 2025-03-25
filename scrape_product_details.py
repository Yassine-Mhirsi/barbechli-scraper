from playwright.sync_api import sync_playwright
import json
import time
import sys
import threading
import queue
import os
from collections import Counter
from scrape_ids import get_product_ids
import data_manager


def get_product_details(id_queue, stop_event):
    """
    Process product details from a queue that's being filled by the ID collector
    
    Args:
        id_queue: Queue containing product IDs to process
        stop_event: Event to signal when ID collection is complete
    """
    # Load existing data
    _, existing_products_dict = data_manager.load_existing_data()
    
    # Initialize counters
    processed = 0
    
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)  # Set to True for production
        page = browser.new_page(viewport={"width": 1000, "height": 400})
        
        # Continue processing as long as we're not stopped and there might be more IDs
        while not stop_event.is_set() or not id_queue.empty():
            try:
                # Get an ID from the queue, wait up to 1 second
                try:
                    product_id = id_queue.get(timeout=1)
                except queue.Empty:
                    # No ID available yet, continue waiting
                    continue
                
                processed += 1
                print(f"\nProcessing product #{processed}: {product_id}")
                
                # Build the product URL
                product_url = f"https://barbechli.tn/product/{product_id}"
                
                # Reset capture flag for this product
                response_captured = False
                product_data = None
                
                # Listen for XHR response events
                def handle_response(response):
                    nonlocal response_captured, product_data
                    url = response.url
                    # Capture the XHR request containing product details
                    if "https://barbechli.tn/find/?q={%22uid" in url:
                        try:
                            xhr_data = response.json()
                            # print(f"Captured product XHR response")
                            # The product data is in the response field
                            if "response" in xhr_data and xhr_data["response"]:
                                product_data = xhr_data["response"]
                                response_captured = True
                        except Exception as e:
                            print(f"Failed to parse response from: {url}")
                            print(f"Error: {e}")
                
                # Set up the response listener
                page.on("response", handle_response)
                
                # Navigate to the product page
                try:
                    page.goto(product_url)
                    
                    # Wait until response is captured
                    wait_start = time.time()
                    timeout = 15  # seconds - shorter for product pages
                    while not response_captured:
                        if time.time() - wait_start > timeout:
                            print(f"Timed out waiting for response for product {product_id}")
                            break
                        page.wait_for_timeout(100)
                    
                    # Process and store the product data if captured
                    if product_data and len(product_data) > 0:
                        # Update the product in our collection
                        updated = data_manager.update_product(existing_products_dict, product_id, product_data)
                        
                        if updated:
                            # Save right away after each product to prevent data loss
                            data_manager.save_products_data(existing_products_dict, is_incremental=True)
                            # print(f"Product saved immediately: {product_id}")
                            
                            # Also do a more comprehensive save every 1 products
                            if processed % 1 == 0:
                                data_manager.save_products_data(existing_products_dict)
                                print(f"Progress milestone: {processed} products processed in this session")
                        else:
                            print(f"No data captured for product {product_id}")
                    else:
                        print(f"No data captured for product {product_id}")
                
                except Exception as e:
                    print(f"Error processing product {product_id}: {e}")
                
                finally:
                    # Remove the event listener to avoid duplicate handlers
                    page.remove_listener("response", handle_response)
                    # Mark task as done
                    id_queue.task_done()
                
            except Exception as e:
                print(f"Error in product processing loop: {e}")
        
        # Close the browser when done
        browser.close()
        print("\nBrowser closed")
    
    # Save all product details one final time
    if existing_products_dict:
        data_manager.save_products_data(existing_products_dict, is_final=True)
    else:
        print("No product details were collected")
    
    return existing_products_dict
