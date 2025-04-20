# Barbechli Web Scraper

A specialized web scraping system for collecting product data from Tunisian e-commerce websites. This project helps gather product information for price comparison purposes.

## Features

- **Multi-store Scraping**: Collect product data from major Tunisian e-stores including Tunisianet, MyTek, and more
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

## Data Storage

Scraped data is stored in:
1. PostgreSQL database (primary storage)
2. JSON files (backup storage):
   - `output/barbechli_product_ids.json`: Contains product IDs
   - `output/barbechli_products_details.json`: Contains complete product details

## [API](api/README.md)

- Docs URL : https://barbechli-api.onrender.com/docs

This project also includes a REST API component that provides access to the scraped data. The API is built with FastAPI and offers endpoints for:

- Browsing products with filtering, sorting, and pagination
- Searching products by various criteria
- Viewing product categories and sources
- Accessing detailed product information

The API is hosted and available for both testing and production use at:
- https://barbechli-api.onrender.com

For more details on the API, including installation, configuration, and available endpoints, please see the [API README](api/README.md).

## [Dashboard](dashboard/README.md)

The project includes an interactive data visualization dashboard built with Dash and Python. The dashboard provides comprehensive insights into the scraped product data through various interactive charts and analyses.

### Key Features

- **Price Distribution Analysis**: Visualize product price distributions across the dataset
- **Brand Price Analysis**: Compare median prices across top brands with min/max ranges
- **Store Price Comparison**: Analyze median prices and product counts across different stores
- **Price Evolution Tracking**: Monitor price changes over time with detailed product information
- **Interactive Visualizations**: All charts feature interactive elements and hover details
- **Responsive Design**: Built with Bootstrap for a clean, modern interface

The dashboard is hosted and accessible online at:
- https://barbechli-scraper-dashboard.onrender.com/

For more details about the dashboard, including local setup and configuration, please see the [Dashboard README](dashboard/README.md).

## License

[MIT License](LICENSE)
