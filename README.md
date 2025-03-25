# Barbechli Price Comparison System

A comprehensive web scraping and API system that collects product data from Tunisian e-commerce websites and provides it through a REST API for Barbechli.tn's price comparison service.

## Web Scraper

The core of the Barbechli system is a powerful web scraper built with Playwright that automatically extracts product information from multiple Tunisian e-commerce websites.

### Scraper Features

- **Multi-store Collection**: Scrapes products from major Tunisian stores including Tunisianet, MyTek, Wiki, Jumia, and others
- **Comprehensive Data Extraction**:
  - Product names, descriptions, and specifications
  - Current and historical prices
  - Categories and subcategories
  - Images and product URLs
  - Availability status
  - Store/seller information
- **Automatic Data Processing**: Normalizes and standardizes data across different sources
- **Scheduled Operation**: Runs at configurable intervals to keep product data current
- **Price History Tracking**: Records price changes over time for trend analysis
- **Efficient Operation**: Uses browser automation with Playwright for reliable scraping

### Scraper Configuration

The scraper can be configured through the `config.py` file:

```python
# How often to run the full scraping cycle (in hours)
SCRAPE_INTERVAL = 24  

# Stores to scrape (True to enable, False to disable)
STORES = {
    "tunisianet": True,
    "mytek": True,
    # Add more stores as needed
}
```

### Running the Scraper

To execute the scraper:

```bash
python -m scraper.main
```

This will start the scraping process for all enabled stores in the configuration.

## REST API

All data collected by the scraper is accessible through a FastAPI-based REST API. The API provides endpoints for product listing, searching, filtering, and retrieving statistical information.

For detailed information about the API, including endpoints, request parameters, and response formats, please refer to the [API README](api/README.md).


## Technology Stack

- **Web Scraping**: Playwright for browser automation
- **Database**: PostgreSQL (Neon)
- **API**: FastAPI
- **Data Processing**: SQLAlchemy ORM
- **Documentation**: Swagger UI and ReDoc

## Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL database (or Neon PostgreSQL)
- pip and virtualenv

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Yassine-Mhirsi/barbechli-scraper.git
cd barbechli
```

2. Create and activate a virtual environment:
```bash
python -m venv env
# On Windows
env\Scripts\activate
# On macOS/Linux
source env/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the database connection:
   - Copy `config.py.example` to `config.py`
   - Add your database connection string as `NEON_URI`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 