# Barbechli API

A FastAPI-based REST API for the Barbechli price comparison service.

## Features

- Product listing with filtering, sorting, and pagination
- Product search functionality 
- Category and subcategory browsing
- Source/store statistics
- Detailed product information with price history

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure database:

The API uses the same Neon PostgreSQL database as the scraper. Make sure the `config.py` file at the project root contains the `NEON_URI` variable.

## Running the API

Start the API server:

```bash
python run.py
```

The API will be available at http://localhost:8000.

## API Documentation

Interactive API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Products

- `GET /api/v1/products` - List products with filtering options
- `GET /api/v1/products/{product_id}` - Get specific product details
- `GET /api/v1/products/search` - Search products by query
- `GET /api/v1/products/category/{category}` - List products by category
- `GET /api/v1/products/source/{source_name}` - List products by source/store

### Statistics

- `GET /api/v1/stats` - Get system-wide statistics
- `GET /api/v1/stats/categories` - Get all categories and subcategories
- `GET /api/v1/stats/sources` - Get all sources with statistics
- `GET /api/v1/stats/brands` - Get all available brands

### Status

- `GET /` - API root with status info
- `GET /health` - Health check endpoint 