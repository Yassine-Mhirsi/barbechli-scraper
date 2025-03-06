# Barbechli.tn Web Scraper

A multi-threaded web scraper built with Python and Playwright to extract product data from barbechli.tn.

## Features

- Collects product IDs and details concurrently using a producer-consumer pattern
- Saves progress automatically during execution
- Comprehensive logging to track the scraping process

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
pip install playwright
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
   - Start collecting product IDs from the specified category
   - Process product details concurrently
   - Save results to `all_products.json`
   - Create a log file `scraper.log`

3. To change the category being scraped, edit the `category` variable in the `main.py` file:

```python
category = "fashion_beauty"  # Change to your desired category
```

4. To adjust the number of concurrent threads, modify the `NUM_CONSUMERS` variable:

```python
NUM_CONSUMERS = 2  # Increase for faster scraping (with more resources)
```

## Output

- `all_products.json`: Contains all scraped product data
- `scraper.log`: Detailed log of the scraping process

## Notes

- The browser will be visible during execution (headless=False)
- The script may take some time to complete depending on the number of products
- Be respectful of the website's resources and consider adding delays between requests

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


## Troubleshooting

If you encounter any issues:

1. Check the `scraper.log` file for error messages
2. Ensure you have a stable internet connection
3. Try reducing the number of concurrent threads
4. Make sure your IP hasn't been blocked by the website 