import logging
from fastapi import FastAPI, HTTPException, Request
from pymongo import MongoClient
from pydantic import BaseModel, field_validator
from typing import List, Optional


app = FastAPI()

# MongoDB connection
MONGO_URI = 'mongodb+srv://nrsm301:connection-pass@scraper-ordinateurs.aic8d.mongodb.net/?retryWrites=true&w=majority&appName=scraper-ordinateurs&ssl=true'
client = MongoClient(MONGO_URI)
db = client["barbechli_db"]
collection = db["mytek_laptops_test"]


# Pydantic model for product data

class PriceTableEntry(BaseModel):
    date_price: str
    price: float

class AvailabilityTableEntry(BaseModel):
    date_availability: str
    availability: str

class Product(BaseModel):
    uniqueID: str
    title: str
    summary: str
    currency: str
    price: float
    price_min: float
    price_max: float
    price_drop: float
    price_drop_percent: float
    price_week_changed: str
    price_week_drop: float
    price_week_drop_percent: float
    price_deal: str
    price_hot_deal: str
    price_top_deal: str
    link: str
    category: str
    subcategory: str
    source_name: str
    source_link: str
    brand: str
    model: str
    gender: str
    color: str
    material: str
    store: str
    store_label: str
    store_description: str
    delivery: str
    delivery_description: str
    availability: str
    clicks: int
    clicksExternal: int
    reviewsNumber: int
    reviewsValue: float
    priceTable: List[PriceTableEntry]
    availabilityTable: List[AvailabilityTableEntry]
    image: str
    date_creation: str
    imageSearch: str
    
    # @field_validator('price')
    # def parse_price(cls, value):
    #     if isinstance(value, str):
    #         return float(value.replace(',', ''))  # Handle strings like "999,99"
    #     return value

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/products")
async def add_product(product: Product, request: Request):
    logger.info(f"Incoming request body: {await request.json()}")
    try:
        collection.insert_one(product.dict())
        return {"message": "Product added successfully"}
    except Exception as e:
        logger.error(f"Error inserting product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# GET endpoint to retrieve all products
@app.get("/products")
async def get_products():
    try:
        products = list(collection.find({}, {"_id": 0}))
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))