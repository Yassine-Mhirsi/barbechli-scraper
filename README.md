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
- Product statistics generation
- Command-line interface for easy configuration

## Prerequisites

- Python 3.9+
- pip (Python package installer)

## Installation

1. Clone this repository or download the source code:

```bash
git clone git@github.com:Yassine-Mhirsi/barbechli-scraper.git
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
pip install playwright
```

6. Install Playwright browsers:

```bash
playwright install chromium
```

## Usage

### Command-Line Interface

The scraper now provides a command-line interface for easy configuration:

```bash
python run_scraper.py --text "mytek" --sources "mytek" --subcategories "laptops" --output "products.json" --threads 5
```

#### Available Arguments:

- `--text`: Store name for search (e.g., "mytek", "tunisianet")
- `--sources`: Store identifier (e.g., "mytek", "tunisianet")
- `--subcategories`: Category to scrape (default: "laptops")
- `--output`: Output file name (default: "products.json")
- `--threads`: Number of consumer threads (default: 5)

If `--text` or `--sources` is not provided, you will be prompted to enter them.

### Using as a Module

You can also import and use the scraper in your own Python code:

```python
from main import run_scraper

# Run the scraper with custom parameters
products_count = run_scraper(
    text="mytek",
    sources="mytek",
    subcategories="laptops",
    num_consumers=5,
    output_file="products.json"
)

print(f"Scraped {products_count} products")
```

## Output

The scraper saves all products to a single JSON file with the following structure:

```json
{
    "stats": {
        "total_products": 42,
        "total_sources": 3,
        "sources": [
            {
                "name": "mytek",
                "products": 20,
                "percentage": 47.62
            },
            {
                "name": "tunisianet",
                "products": 15,
                "percentage": 35.71
            },
            {
                "name": "mediavision",
                "products": 7,
                "percentage": 16.67
            }
        ]
    },
    "products": [
        {
            "uniqueID": "...",
            "title": "...",
            "store_label": "...",
            "category": "...",
            "subcategory": "...",
            "source_name": "...",
            "image": "...",
            "currency": "...",
            "price": 0,
            "link": "...",
            "availability": "...",
            "date_creation": "..."
            // ... other product fields
        },
        // ... more products
    ]
}
```

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
   - Generates statistics about the collected products

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
