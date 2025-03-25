from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, asc

from app.db.database import get_db
from app.models.product import Product, PriceHistory, AvailabilityHistory
from app.schemas.product import Product as ProductSchema
from app.schemas.product import ProductList, ProductSearchParams
from app.core.config import settings

router = APIRouter()


def convert_db_to_schema(db_product):
    """
    Convert a database Product model to a Pydantic schema Product model
    """
    # Get price history
    price_history = [
        {"date_price": ph.recorded_at, "price": ph.price}
        for ph in db_product.price_history
    ]
    
    # Get availability history
    availability_history = [
        {"date_availability": ah.recorded_at, "availability": ah.availability}
        for ah in db_product.availability_history
    ]
    
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


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: str = Path(..., description="The unique ID of the product"),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific product
    """
    db_product = db.query(Product).filter(Product.unique_id == product_id).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return convert_db_to_schema(db_product)


@router.get("/search/", response_model=ProductList)
async def search_products(
    params: ProductSearchParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Advanced search for products with multiple criteria
    """
    # Start with a base query
    query = db.query(Product)
    
    # Apply search filter if provided
    if params.q:
        search_pattern = f"%{params.q}%"
        query = query.filter(or_(
            Product.title.ilike(search_pattern),
            Product.brand.ilike(search_pattern),
            Product.category.ilike(search_pattern),
            Product.subcategory.ilike(search_pattern)
        ))
    
    # Apply other filters if provided
    if params.category:
        query = query.filter(Product.category == params.category)
    
    if params.subcategory:
        query = query.filter(Product.subcategory == params.subcategory)
    
    if params.source_name:
        query = query.filter(Product.source_name == params.source_name)
    
    if params.brand:
        query = query.filter(Product.brand == params.brand)
    
    if params.min_price is not None:
        query = query.filter(Product.current_price >= params.min_price)
    
    if params.max_price is not None:
        query = query.filter(Product.current_price <= params.max_price)
    
    if params.availability:
        query = query.filter(Product.availability == params.availability)
    
    # Apply sorting
    sort_column = getattr(Product, params.sort_by, Product.last_updated)
    if params.sort_order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    # Get total count for pagination info
    total = query.count()
    
    # Ensure limit is properly applied
    actual_limit = min(params.limit, settings.MAX_PAGE_SIZE)
    
    # Apply pagination
    query = query.offset(params.skip).limit(actual_limit)
    
    # Execute query
    db_products = query.all()
    
    # Convert database models to schema models
    products = [convert_db_to_schema(product) for product in db_products]
    
    # Return products
    return {
        "total": total,
        "items": products
    }


@router.get("/category/{category}", response_model=ProductList)
async def list_products_by_category(
    category: str = Path(..., description="Category name"),
    subcategory: Optional[str] = Query(None, description="Subcategory name"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    List products by category with optional subcategory filter
    """
    # Start with a base query
    query = db.query(Product).filter(Product.category == category)
    
    # Apply subcategory filter if provided
    if subcategory:
        query = query.filter(Product.subcategory == subcategory)
    
    # Get total count for pagination info
    total = query.count()
    
    # Apply sorting by most recent first
    query = query.order_by(desc(Product.last_updated))
    
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


@router.get("/source/{source_name}", response_model=ProductList)
async def list_products_by_source(
    source_name: str = Path(..., description="Source name"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    List products by source/store
    """
    # Start with a query filtered by source
    query = db.query(Product).filter(Product.source_name == source_name)
    
    # Get total count for pagination info
    total = query.count()
    
    # Apply sorting by most recent first
    query = query.order_by(desc(Product.last_updated))
    
    # Explicitly set the limit and skip values
    actual_limit = min(limit, settings.MAX_PAGE_SIZE)
    
    # Apply pagination
    query = query.offset(skip).limit(actual_limit)
    
    # Log for debugging
    print(f"Source: {source_name}, Skip: {skip}, Limit: {actual_limit}, Total: {total}")
    
    # Execute query with explicit limit
    db_products = query.all()
    
    print(f"Retrieved {len(db_products)} products")
    
    # Convert database models to schema models
    products = [convert_db_to_schema(product) for product in db_products]
    
    # Return products
    return {
        "total": total,
        "items": products
    } 