# Barbechli Price Comparison System

A comprehensive web scraping and API system that collects product data from Tunisian e-commerce websites and provides it through a REST API for Barbechli.tn's price comparison service.

## Project Structure

```
barbechli/
├── api/                  # FastAPI application
│   ├── app/
│   │   ├── api/          # API routes
│   │   │   └── v1/       # API v1 endpoints
│   │   ├── core/         # Core configuration
│   │   ├── db/           # Database connection
│   │   ├── models/       # SQLAlchemy models
│   │   └── schemas/      # Pydantic schemas
│   ├── README.md         # API-specific README
│   └── run.py            # Script to run the API
├── scraper/              # Web scraping modules
│   ├── stores/           # Store-specific scrapers
│   ├── utils/            # Utility functions
│   └── main.py           # Main scraping script
├── config.py             # Configuration file
└── README.md             # Main README file
```

## Features

### Scraper Features
- Multi-store scraping from major Tunisian e-commerce websites
- Automated data extraction for products, including:
  - Names, descriptions, and specifications
  - Prices and price history
  - Categories and subcategories
  - Images and URLs
  - Availability status
  - Seller information
- Scheduled scraping to keep data up-to-date

### API Features
- Product listing with filtering, sorting, and pagination
- Advanced product search by various criteria
- Category and subcategory browsing
- Detailed product information with price history
- Store/source statistics
- Auto-generated API documentation

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
git clone https://github.com/yourusername/barbechli.git
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
   - Create a `config.py` file in the root directory
   - Add your database connection string as `NEON_URI`

### Running the API

Navigate to the API directory and run the application:
```bash
cd api
python run.py
```

The API will be available at http://localhost:8000. You can access:
- API documentation: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

### Running the Scraper

Execute the scraper module:
```bash
python -m scraper.main
```

## Documentation

- API documentation is available at `/docs` endpoint when the API is running
- The `/api/README.md` file contains detailed information about the API endpoints and usage

## Project Structure

```
barbechli/
├── api/                  # FastAPI application
│   ├── app/
│   │   ├── api/          # API routes
│   │   │   └── v1/       # API v1 endpoints
│   │   ├── core/         # Core configuration
│   │   ├── db/           # Database connection
│   │   ├── models/       # SQLAlchemy models
│   │   └── schemas/      # Pydantic schemas
│   ├── README.md         # API-specific README
│   └── run.py            # Script to run the API
├── scraper/              # Web scraping modules
│   ├── stores/           # Store-specific scrapers
│   ├── utils/            # Utility functions
│   └── main.py           # Main scraping script
├── config.py             # Configuration file
└── README.md             # Main README file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 