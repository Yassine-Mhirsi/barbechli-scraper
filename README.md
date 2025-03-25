# Barbechli Web Scraper

A specialized web scraping system for collecting product data from Tunisian e-commerce websites. This project helps gather product information for price comparison purposes.

## Features

- **Multi-store Scraping**: Collect product data from major Tunisian e-stores including Tunisianet, MyTek, Wiki, Jumia, and more
- **Concurrent Processing**: Uses threading for simultaneous collection of product IDs and details
- **Data Persistence**: Stores scraped data in both PostgreSQL database and JSON files
- **Historical Price Tracking**: Records price changes over time
- **Comprehensive Product Details**: Collects product names, prices, descriptions, images, availability, and more

## Requirements

- Python 3.9+
- PostgreSQL database (Neon PostgreSQL recommended)
- Playwright for browser automation

## Installation

1. Clone the repository
```bash
git clone https://github.com/Yassine-Mhirsi/barbechli-scraper.git
cd barbechli-scraper
```

2. Install the required dependencies
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers
```bash
playwright install
```

4. Configure the application
```bash
cp config.py.example config.py
# Edit config.py with your database credentials and scraper settings
```

## Usage

### Basic Usage

Run the main scraper:

```bash
python main.py
```

This will start two concurrent processes:
- Product ID collection
- Product detail scraping

### Customizing Scraping Parameters

You can customize the scraping parameters in `main.py`:

```python
# Example parameters for product search
params = {
    "text": "ordinateur portable",
    "category": "computers",
    "subcategories": "laptops",
    "sources": "tunisianet"
}
```

Available parameters:
- `text`: Search query
- `category`: Product category
- `subcategories`: Specific subcategories
- `sources`: Specific e-commerce stores
- `orderby`: Sorting order (default: popularity)

## Project Structure

- `scrape_ids.py`: Collects product IDs from search results
- `scrape_product_details.py`: Extracts detailed product information
- `data_manager.py`: Manages product data formatting and persistence
- `db_manager.py`: Handles database operations
- `main.py`: Main entry point that coordinates the scraping processes
- `config.py`: Configuration settings

## Data Storage

Scraped data is stored in:
1. PostgreSQL database (primary storage)
2. JSON files (backup storage):
   - `output/barbechli_product_ids.json`: Contains product IDs
   - `output/barbechli_products_details.json`: Contains complete product details

## [API](api/README.md)

This project also includes a REST API component that provides access to the scraped data. The API is built with FastAPI and offers endpoints for:

- Browsing products with filtering, sorting, and pagination
- Searching products by various criteria
- Viewing product categories and sources
- Accessing detailed product information

For more details on the API, including installation, configuration, and available endpoints, please see the [API README](api/README.md).

## License

[MIT License](LICENSE)
