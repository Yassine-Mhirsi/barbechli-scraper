from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.db.database import get_db
from app.models.product import Product
from app.schemas.product import ProductList
from app.core.config import settings

router = APIRouter()


def convert_db_to_schema(db_product):
    """
    Convert a database Product model to a Pydantic schema Product model
    """
    # Get price history from JSONB column
    price_history = db_product.price_history if db_product.price_history else []
    
    # Get availability history from JSONB column
    availability_history = db_product.availability_history if db_product.availability_history else []
    
    # Create the schema model
    return {
        "uniqueID": db_product.unique_id,
        "title": db_product.title,
        "store_label": db_product.store_label,
        "category": db_product.category,
        "subcategory": db_product.subcategory,
        "source_name": db_product.source_name,
        "image": db_product.image_url,
        "currency": db_product.currency,
        "price": db_product.current_price,
        "brand": db_product.brand,
        "availability": db_product.availability,
        "link": db_product.link,
        "source_link": db_product.source_link,
        "clicks": db_product.clicks,
        "clicksExternal": db_product.clicks_external,
        "date_creation": db_product.date_creation,
        "last_updated": db_product.last_updated,
        "priceTable": price_history,
        "availabilityTable": availability_history
    }


@router.get("/", response_model=ProductList)
async def list_products(
    q: Optional[str] = Query(None, description="Search query for product title"),
    uniqueid: Optional[str] = Query(None, description="Filter by product unique ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory"),
    source_name: Optional[str] = Query(None, description="Filter by source name"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    availability: Optional[str] = Query(None, description="Filter by availability status"),
    sort_by: str = Query("last_updated", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    List products with filtering, sorting and pagination
    """
    # Start with a base query
    query = db.query(Product)
    
    # Apply filters if provided
    if q:
        search_pattern = f"%{q}%"
        query = query.filter(Product.title.ilike(search_pattern))
    
    if uniqueid:
        query = query.filter(Product.unique_id == uniqueid)
    
    if category:
        query = query.filter(Product.category == category)
    
    if subcategory:
        query = query.filter(Product.subcategory == subcategory)
    
    if source_name:
        query = query.filter(Product.source_name == source_name)
    
    if brand:
        query = query.filter(Product.brand == brand)
    
    if min_price is not None:
        query = query.filter(Product.current_price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.current_price <= max_price)
    
    if availability:
        query = query.filter(Product.availability == availability)
    
    # Apply sorting
    sort_column = getattr(Product, sort_by, Product.last_updated)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    # Get total count for pagination info
    total = query.count()
    
    # Ensure limit is properly applied
    actual_limit = min(limit, settings.MAX_PAGE_SIZE)
    
    # Apply pagination
    query = query.offset(skip).limit(actual_limit)
    
    # Execute query
    db_products = query.all()
    
    # Convert database models to schema models
    products = [convert_db_to_schema(product) for product in db_products]
    
    # Return products
    return {
        "total": total,
        "items": products
    } 