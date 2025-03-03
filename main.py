from playwright.sync_api import sync_playwright
import json
from typing import List, Optional
import logging

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

def get_product_ids(category: str) -> List[str]:
    product_ids = []
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

        page = context.new_page()
        page_number = 1
        has_more_pages = True

        while has_more_pages:
            response_data = None
            logging.info(f"Processing page {page_number}")

            def handle_category_request(request):
                if (request.resource_type == "xhr" and 
                    f'https://barbechli.tn/find/?q={{%22category%22:[%22{category}%22],%22key%' in request.url and 
                    f',%22orderby%22:{{%22type%22:%22popularity%22,%22direction%22:%22desc%22,%22desc%22:%22popularity%22}},%22pages%22:{{%22number%22:{page_number},%22rows%22:24}}}}' in request.url):
                    logging.debug(f"Found matching XHR request on page {page_number}")
                    response = request.response()
                    if response:
                        try:
                            nonlocal response_data
                            response_data = json.loads(response.text())
                            page.close()
                        except Exception as e:
                            logging.error(f"Error capturing response on page {page_number}: {str(e)}")

            page = context.new_page()
            page.on('request', handle_category_request)

            try:
                url = f"https://barbechli.tn/search;category={category};orderby=popularity;pagenumber={page_number}"
                page.goto(url)
                page.wait_for_timeout(2000)  # Wait for XHR to complete
            except Exception as e:
                if "Target page, context or browser has been closed" not in str(e):
                    print(f"An error occurred: {e}")

            if response_data:
                if "status" in response_data and response_data["status"].get("code") == "ERROR_ELASTIC":
                    logging.info("Reached end of available pages")
                    has_more_pages = False
                else:
                    new_ids = [product["uniqueID"] for product in response_data.get("response", []) if "uniqueID" in product]
                    product_ids.extend(new_ids)
                    logging.info(f"Found {len(new_ids)} products on page {page_number}. Total products so far: {len(product_ids)}")
                    page_number += 1
            else:
                logging.warning(f"No response data received for page {page_number}")
                has_more_pages = False

        context.close()
        browser.close()
        logging.info(f"Finished collecting product IDs. Total products found: {len(product_ids)}")

    return product_ids

def get_product_details(product_id: str) -> Optional[dict]:
    logging.info(f"Fetching details for product ID: {product_id}")
    
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

        page = context.new_page()
        response_body = None

        def handle_request(request):
            if request.resource_type == "xhr" and 'https://barbechli.tn/find/?q={%22uid' in request.url:
                response = request.response()
                if response:
                    try:
                        nonlocal response_body
                        response_body = json.loads(response.text())
                        logging.debug(f"Successfully captured response for product {product_id}")
                        page.close()
                    except Exception as e:
                        logging.error(f"Error capturing response for product {product_id}: {str(e)}")

        page.on('request', handle_request)

        try:
            page.goto(f"https://barbechli.tn/product/{product_id}")
            page.wait_for_timeout(2000)  # Wait for XHR to complete
        except Exception as e:
            if "Target page, context or browser has been closed" not in str(e):
                print(f"An error occurred: {e}")

        if not response_body:
            logging.warning(f"No response body received for product {product_id}")
        
        context.close()
        browser.close()
        return response_body

if __name__ == "__main__":
    logging.info("Starting scraping process")
    category = "fashion_beauty"
    
    # Get all product IDs
    product_ids = get_product_ids(category)
    logging.info(f"Found {len(product_ids)} products to process")
    
    # Get details for each product
    all_products = []
    for idx, product_id in enumerate(product_ids, 1):
        logging.info(f"Processing product {idx}/{len(product_ids)}")
        product_details = get_product_details(product_id)
        if product_details:
            all_products.append(product_details)
        else:
            logging.warning(f"Failed to get details for product {product_id}")
    
    # Save all products to a file
    output_file = 'all_products.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    
    logging.info(f"Scraping completed. Saved {len(all_products)} products to {output_file}")