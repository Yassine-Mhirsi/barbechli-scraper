# Barbechli.tn Web Scraper

A multi-threaded web scraper built with Python and Playwright to extract product data from barbechli.tn, focusing on specific stores and categories.

## Features

- Multi-threaded architecture with producer-consumer pattern
- Store-specific product scraping (Tunisianet, Mytek, Mediavision, etc.)
- Automatic retry system for failed requests (3 attempts)
- Smart pagination with end-of-results detection
- Headless browser operation for faster scraping
- Dynamic output filenames based on store and category
- Comprehensive logging and error handling
- Automatic progress saving

## Prerequisites

- Python 3.9+
- pip (Python package installer)

## Installation

1. Clone this repository or download the source code && Navigate to the project directory:

```bash
git clone git@github.com:Yassine-Mhirsi/barbechli-scraper.git
cd barbechli-scraper
```

2. Create and Activate virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install playwright
playwright install chromium
```


## Usage

1. Configure the scraper in `main.py`:

```python
# Set the store and category to scrape
text = "mytek"          # Store name for search
sources = "mytek"       # Store identifier
subcategories = "laptops"  # Category to scrape

# Adjust number of concurrent threads if needed
NUM_CONSUMERS = 5  # Increase for faster scraping
```

2. Run the scraper:

```bash
python main.py
```

3. The script will:
   - Start collecting product IDs from the specified store and category
   - Process product details concurrently using multiple threads
   - Save results to `<store>_<category>.json` (e.g., `mytek_laptops.json`)
   - Create a detailed log file `scraper.log`

## Output

- `<store>_<category>.json`: Contains all scraped product data
- `scraper.log`: Detailed log of the scraping process, including:
  - Page processing status
  - Retry attempts
  - Product counts
  - Error messages

## How It Works

The scraper operates in three main stages using a multi-threaded approach:

1. **Product ID Collection (Producer Thread)**
   - Navigates to store-specific category pages
   - Intercepts XHR requests to capture product IDs
   - Implements smart pagination with retry system
   - Detects end of available products through multiple checks

2. **Product Details Extraction (Consumer Threads)**
   - Multiple threads process product IDs concurrently
   - Each thread handles individual product pages
   - Captures detailed product information from XHR responses
   - Adds data to thread-safe collection

3. **Data Saving (Saver Thread)**
   - Periodically saves progress to JSON file
   - Uses dynamic filenames based on store and category
   - Ensures no data loss in case of interruption

## Performance Features

- Headless browser operation for faster processing
- Configurable number of consumer threads
- Automatic retry system (3 attempts) for failed requests
- Smart pagination with multiple end-of-results checks:
  - ERROR_ELASTIC status detection
  - Empty results detection
  - Partial page detection (< 24 products)
- 2-second delay between retry attempts

## Notes

- The scraper runs in headless mode for better performance
- Processing time depends on number of products and threads
- Consider website load when adjusting thread count
- Automatic retries help handle temporary network issues

## Troubleshooting

If you encounter any issues:

1. Check the `scraper.log` file for detailed error messages
2. Ensure stable internet connection
3. Try reducing the number of consumer threads
4. Verify the store and category parameters
5. Check if the website is blocking automated access 


# API Endpoints

## Installation 
see updated requirements.txt

## Usage

to start Up FastAPI Server run the command:
uvicorn api:app --reload

open your browser and navigate to http://127.0.0.1:8000/products
