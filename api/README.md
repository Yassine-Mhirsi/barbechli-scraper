# Barbechli API

A FastAPI-based REST API for the Barbechli price comparison service.

## Features

- Product listing with comprehensive filtering options
- Sorting and pagination support
- Price and availability history tracking
- Source/store statistics

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure database:

The API uses the same Neon PostgreSQL database as the scraper. Make sure the `env` file at the project root contains the `NEON_URI` variable.

## Running the API

### Local Development

Start the API server locally:

```bash
python run.py
```

The API will be available at http://localhost:8000.

### Production

The API is hosted and available for both testing and production use at:
- https://barbechli-api.onrender.com/docs

The production API includes:
- Automatic keep-alive mechanism
- Continuous uptime monitoring
- Regular health checks

## API Documentation

Interactive API documentation is available at:

- Swagger UI: https://barbechli-api.onrender.com/docs
- ReDoc: https://barbechli-api.onrender.com/redoc

## API Endpoints

### Products

`GET /api/v1/products` - List products with comprehensive filtering options:

Query Parameters:
- `q`: Search query for product title
- `uniqueid`: Filter by product unique ID
- `category`: Filter by category
- `subcategory`: Filter by subcategory
- `source_name`: Filter by source/store name
- `brand`: Filter by brand
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `availability`: Filter by availability status
- `sort_by`: Field to sort by (default: last_updated)
- `sort_order`: Sort order - "asc" or "desc" (default: desc)
- `skip`: Number of records to skip (pagination)
- `limit`: Number of records to return (pagination)

Example usage:
```
GET /api/v1/products?q=laptop&category=electronics&min_price=500&max_price=1000&sort_by=price&sort_order=asc&limit=10
```

### Statistics

- `GET /api/v1/stats` - Get system-wide statistics
- `GET /api/v1/stats/categories` - Get all categories and subcategories
- `GET /api/v1/stats/sources` - Get all sources with statistics
- `GET /api/v1/stats/brands` - Get all available brands

### Status

- `GET /` - API root with status info
- `GET /health` - Health check endpoint 