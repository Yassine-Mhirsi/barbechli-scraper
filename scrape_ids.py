from playwright.sync_api import sync_playwright
import json
import re
import sys
import time

def get_product_ids(params=None, start_page=1):
    """
    Capture XHR response from Barbechli website with automatic pagination,
    collecting only the uniqueID of each product
    
    Args:
        params (dict): Dictionary of URL parameters. Available keys:
            - category: Product category
            - text: Search text
            - subcategories: Specific subcategories
            - sources: Specific sources/sellers
            - orderby: Sorting order (default: popularity)
        start_page (int): The page number to start scraping from (default: 1)
    """
    # Set default parameters if none provided
    if params is None:
        params = {}
    
    # Set default values for required parameters
    if "orderby" not in params:
        params["orderby"] = "popularity"
    
    # Initialize collected data
    all_unique_ids = []
    current_page = start_page
    last_page_reached = False
    
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)  # Set to True for production
        page = browser.new_page(viewport={"width": 1000, "height": 400})
        
        while not last_page_reached:
            # Update page number parameter
            params["pagenumber"] = str(current_page)
            
            # Build the URL with parameters
            base_url = "https://barbechli.tn/search"
            url_parts = []
            
            for key, value in params.items():
                url_parts.append(f"{key}={value}")
            
            full_url = base_url + ";" + ";".join(url_parts)
            print(f"\nScraping page {current_page}: {full_url}")
            
            # Reset capture flag for this page
            response_captured = False
            page_products = None
            
            # Listen for response events
            def handle_response(response):
                nonlocal response_captured, page_products
                url = response.url
                if "https://barbechli.tn/find/?q=" in url and "orderby" in url:
                    try:
                        xhr_data = response.json()
                        print(f"Captured XHR response")
                        # Extract products from the response
                        if "response" in xhr_data:
                            page_products = xhr_data["response"]
                            response_captured = True
                    except Exception as e:
                        print(f"Failed to parse response from: {url}")
                        print(f"Error: {e}")
            
            # Set up the response listener
            page.on("response", handle_response)
            
            # Navigate to the page
            page.goto(full_url)
            
            # Wait until response is captured
            wait_start = time.time()
            timeout = 30  # seconds
            while not response_captured:
                if time.time() - wait_start > timeout:
                    print(f"Timed out waiting for response on page {current_page}")
                    break
                page.wait_for_timeout(100)
            
            # Remove the event listener to avoid duplicate handlers
            page.remove_listener("response", handle_response)
            
            # Check if we've reached the last page (empty response)
            if page_products is not None:
                if len(page_products) == 0:
                    print(f"Reached last page at page {current_page} (empty response)")
                    last_page_reached = True
                else:
                    # Extract only uniqueID from each product
                    page_unique_ids = []
                    for product in page_products:
                        if "uniqueID" in product:
                            page_unique_ids.append(product["uniqueID"])
                    
                    # print(f"Found {len(page_unique_ids)} product IDs on page {current_page}")
                    all_unique_ids.extend(page_unique_ids)
                    
                    # Save progress after each page
                    with open("barbechli_product_ids.json", "w", encoding="utf-8") as f:
                        json.dump(all_unique_ids, f, indent=2, ensure_ascii=False)
                    print(f"Total product IDs collected so far: {len(all_unique_ids)}")
                    
                    # Move to next page
                    current_page += 1
            else:
                print(f"No response captured for page {current_page}, stopping")
                last_page_reached = True
        
        # Close the browser when done
        browser.close()
        print("\nBrowser closed")
        
        # Final save of all product IDs
        if all_unique_ids:
            with open("barbechli_product_ids.json", "w", encoding="utf-8") as f:
                json.dump(all_unique_ids, f, indent=2, ensure_ascii=False)
            print(f"All product IDs saved to barbechli_product_ids.json")
            print(f"Total product IDs collected: {len(all_unique_ids)}")
        else:
            print("No product IDs were collected")
        
        return all_unique_ids

def collect_ids_thread(id_queue, stop_event, params=None, start_page=1):
    """
    Thread function that collects product IDs and adds them to the queue
    as they are found, for immediate processing by the product details scraper.
    
    Args:
        id_queue: Queue to put product IDs in
        stop_event: Event to signal when ID collection is complete
        params: Parameters for the product search
        start_page: Page to start collection from
    """
    # Set default parameters if none provided
    if params is None:
        params = {}
    
    # Set default values for required parameters
    if "orderby" not in params:
        params["orderby"] = "popularity"
    
    # Track progress
    total_ids_found = 0
    all_ids = []  # Keep track of all IDs for a single backup file
    current_page = start_page
    last_page_reached = False
    
    try:
        with sync_playwright() as p:
            # Launch the browser
            browser = p.chromium.launch(headless=False)  # Set to True for production
            page = browser.new_page(viewport={"width": 1000, "height": 400})
            
            while not last_page_reached and not stop_event.is_set():
                # Update page number parameter
                params["pagenumber"] = str(current_page)
                
                # Build the URL with parameters
                base_url = "https://barbechli.tn/search"
                url_parts = []
                
                for key, value in params.items():
                    url_parts.append(f"{key}={value}")
                
                full_url = base_url + ";" + ";".join(url_parts)
                print(f"\nScraping page {current_page}: {full_url}")
                
                # Reset capture flag for this page
                response_captured = False
                page_products = None
                
                # Listen for response events
                def handle_response(response):
                    nonlocal response_captured, page_products
                    url = response.url
                    if "https://barbechli.tn/find/?q=" in url and "orderby" in url:
                        try:
                            xhr_data = response.json()
                            print(f"Captured XHR response")
                            # Extract products from the response
                            if "response" in xhr_data:
                                page_products = xhr_data["response"]
                                response_captured = True
                        except Exception as e:
                            print(f"Failed to parse response from: {url}")
                            print(f"Error: {e}")
                
                # Set up the response listener
                page.on("response", handle_response)
                
                # Navigate to the page
                page.goto(full_url)
                
                # Wait until response is captured
                wait_start = time.time()
                timeout = 30  # seconds
                while not response_captured:
                    if time.time() - wait_start > timeout:
                        print(f"Timed out waiting for response on page {current_page}")
                        break
                    page.wait_for_timeout(100)
                
                # Remove the event listener to avoid duplicate handlers
                page.remove_listener("response", handle_response)
                
                # Check if we've reached the last page (empty response)
                if page_products is not None:
                    if len(page_products) == 0:
                        print(f"Reached last page at page {current_page} (empty response)")
                        last_page_reached = True
                    else:
                        # Process each product and add its ID to the queue immediately
                        page_ids_count = 0
                        for product in page_products:
                            if "uniqueID" in product:
                                product_id = product["uniqueID"]
                                # Add to queue for immediate processing
                                id_queue.put(product_id)
                                # Also add to our complete list for backup
                                all_ids.append(product_id)
                                page_ids_count += 1
                                total_ids_found += 1
                        
                        print(f"Added {page_ids_count} product IDs to queue from page {current_page}")
                        print(f"Total product IDs collected so far: {total_ids_found}")
                        
                        # Save all IDs to a single backup file periodically
                        if current_page % 3 == 0:  # Save every 3 pages to avoid excessive disk writes
                            try:
                                with open("barbechli_product_ids.json", "w", encoding="utf-8") as f:
                                    json.dump(all_ids, f, indent=2, ensure_ascii=False)
                                print(f"Saved backup of {len(all_ids)} IDs to barbechli_product_ids.json")
                            except Exception as e:
                                print(f"Error saving IDs to backup file: {e}")
                        
                        # Move to next page
                        current_page += 1
                else:
                    print(f"No response captured for page {current_page}, stopping")
                    last_page_reached = True
            
            # Save final backup of all IDs
            if all_ids:
                try:
                    with open("barbechli_product_ids.json", "w", encoding="utf-8") as f:
                        json.dump(all_ids, f, indent=2, ensure_ascii=False)
                    print(f"Saved final backup of {len(all_ids)} IDs to barbechli_product_ids.json")
                except Exception as e:
                    print(f"Error saving IDs to backup file: {e}")
            
            # Close the browser when done
            browser.close()
            print("\nID collector browser closed")
            
            print(f"Total product IDs added to queue: {total_ids_found}")
    
    except Exception as e:
        print(f"Error in ID collector thread: {e}")
    
    finally:
        # Signal that we're done collecting IDs
        print("ID collection completed, setting stop event")
        stop_event.set()

if __name__ == "__main__":
    # Example of setting dynamic parameters
    params = {
        "text": "ordinateur portable",
        "category": "computers",
        "subcategories": "laptops",
        "sources": "tunisianet"
    }
    
    # Call the function with parameters, starting from page 1
    product_ids = get_product_ids(params, start_page=1)