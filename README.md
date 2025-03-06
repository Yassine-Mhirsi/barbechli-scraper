# Barbechli.tn Web Scraper

A multi-threaded web scraper built with Python and Playwright to extract product data from barbechli.tn, with support for specific stores like Tunisianet.

## Features

- Collects product IDs and details concurrently using a producer-consumer pattern
- Saves progress automatically during execution
- Comprehensive logging to track the scraping process
- Supports scraping specific stores and categories
- Configurable URL parameters for flexible scraping

## How It Works

The scraper operates in three main stages using a multi-threaded approach:

1. **Product ID Collection (Producer Thread)**
   - Navigates to category pages on barbechli.tn
   - Intercepts XHR requests to capture product IDs
   - Places product IDs in a shared queue
   - Handles pagination to collect IDs from all available pages

2. **Product Details Extraction (Consumer Threads)**
   - Multiple threads pull product IDs from the shared queue
   - Each thread visits individual product pages
   - Intercepts XHR responses containing detailed product information
   - Adds complete product data to a shared collection

3. **Data Saving (Saver Thread)**
   - Periodically saves all collected product data to a JSON file
   - Ensures no data is lost if the process is interrupted
   - Performs a final save when all products have been processed

This architecture allows for efficient parallel processing while maintaining a controlled flow of data between threads.

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone this repository or download the source code:

```bash
git clone <repository-url>
# or download and extract the zip file
```

2. Navigate to the project directory:

```bash
cd barbechli-scraper
```

3. Create a virtual environment (recommended):

```bash
python -m venv venv
```

4. Activate the virtual environment:

- On Windows:
```bash
venv\Scripts\activate
```
- On macOS/Linux:
```bash
source venv/bin/activate
```

5. Install the required dependencies:

```bash
pip install -r requirements.txt
```

6. Install Playwright browsers:

```bash
playwright install chromium
```

## Usage

1. Run the scraper:

```bash
python main.py
```

2. The script will:
   - Start collecting product IDs from the specified store and category
   - Process product details concurrently
   - Save results to a JSON file named after the store and category (e.g., `tunisianet_laptops.json`)
   - Create a log file `scraper.log`

3. To change the store or category being scraped, edit the `store_config` dictionary in the `main.py` file:

```python
store_config = {
    'store_name': 'Tunisianet',
    'url_template': 'https://barbechli.tn/search;text={search_text};subcategories={subcategory};sources={source};orderby=popularity;pagenumber={page_number}',
    'search_text': 'Tunisianet',
    'subcategory': 'laptops',
    'source': 'tunisianet'
}
```

4. To scrape a different store, create a new configuration:

```python
# Example for another store
store_config = {
    'store_name': 'AnotherStore',
    'url_template': 'https://barbechli.tn/search;text={search_text};subcategories={subcategory};sources={source};orderby=popularity;pagenumber={page_number}',
    'search_text': 'AnotherStore',
    'subcategory': 'smartphones',
    'source': 'anotherstore'
}
```

5. To adjust the number of concurrent threads, modify the `NUM_CONSUMERS` variable:

```python
NUM_CONSUMERS = 2  # Increase for faster scraping (with more resources)
```

## Output

- `<store_name>_<subcategory>.json`: Contains all scraped product data (e.g., `tunisianet_laptops.json`)
- `scraper.log`: Detailed log of the scraping process

## Notes

- The browser will be visible during execution (headless=False)
- The script may take some time to complete depending on the number of products
- Be respectful of the website's resources and consider adding delays between requests

## Troubleshooting

If you encounter any issues:

1. Check the `scraper.log` file for error messages
2. Ensure you have a stable internet connection
3. Try reducing the number of concurrent threads
4. Make sure your IP hasn't been blocked by the website 