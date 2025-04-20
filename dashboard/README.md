# Barbechli Price Analysis Dashboard

A dynamic web application built with Dash and Python for analyzing and visualizing e-commerce product pricing data.

## Live Demo

The dashboard is deployed and accessible online at:
[https://barbechli-scraper-dashboard.onrender.com/](https://barbechli-scraper-dashboard.onrender.com/)

## Features

- **Price Distribution Analysis**: Visualize the distribution of product prices across the dataset
- **Brand Price Analysis**: Compare median prices across top brands with min/max price ranges
- **Store Price Comparison**: Analyze median prices and product counts across different stores
- **Price Evolution Tracking**: Monitor price changes over time with detailed product information
- **Interactive Visualizations**: All charts feature interactive elements and hover details
- **Responsive Design**: Built with Bootstrap for a clean, modern interface

## Prerequisites

- Python 3.6+
- pip (Python package manager)

## Installation

1. Open directory:
```bash
cd dashboard
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
dashboard/
├── app.py              # Main application entry point
├── pages/              # Dashboard page components
│   └── price.py       # Price analysis page
├── utils/             # Utility functions and helpers
├── assets/            # Static assets (CSS, images)
├── products.csv       # Product data
└── requirements.txt   # Project dependencies
```

## Usage

### Online Access
Visit the live dashboard at [https://barbechli-scraper-dashboard.onrender.com/](https://barbechli-scraper-dashboard.onrender.com/)

### Local Development
1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:10000
```

## Data Format

The dashboard expects a CSV file (`products.csv`) with the following key columns:
- `uniqueID`: Unique identifier for each product
- `title`: Product name/description
- `price`: Current product price
- `brand`: Product brand name
- `store_label`: Store identifier
- `priceTable`: JSON string containing price history data

## License

[MIT License](LICENSE) 
