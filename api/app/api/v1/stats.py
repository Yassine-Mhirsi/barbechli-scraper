from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.db.database import get_db
from app.models.product import Product, SourceStats
from app.schemas.product import StatsResponse, SourceStat

router = APIRouter()


def convert_source_stat(db_source_stat):
    """
    Convert a database SourceStats model to a Pydantic schema SourceStat model
    """
    return {
        "name": db_source_stat.name,
        "products": db_source_stat.products_count,
        "percentage": db_source_stat.percentage
    }


@router.get("/", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """
    Get system-wide statistics about products and sources
    """
    # Get total product count
    total_products = db.query(func.count(Product.id)).scalar() or 0
    
    # Get source statistics
    db_source_stats = db.query(SourceStats).order_by(SourceStats.products_count.desc()).all()
    
    # Convert to schema models
    source_stats = [convert_source_stat(source) for source in db_source_stats]
    
    # Format response
    return {
        "total_products": total_products,
        "total_sources": len(source_stats),
        "sources": source_stats
    }


@router.get("/categories", response_model=Dict[str, List[str]])
async def get_categories(db: Session = Depends(get_db)):
    """
    Get all available categories and subcategories
    """
    # Get distinct categories
    categories = db.query(distinct(Product.category)).filter(Product.category.isnot(None)).all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    # For each category, get its subcategories
    result = {}
    for category in categories:
        subcategories = db.query(distinct(Product.subcategory))\
            .filter(Product.category == category)\
            .filter(Product.subcategory.isnot(None))\
            .all()
        subcategories = [subcat[0] for subcat in subcategories if subcat[0]]
        result[category] = subcategories
    
    return result


@router.get("/sources", response_model=List[SourceStat])
async def get_sources(db: Session = Depends(get_db)):
    """
    Get all available sources/stores with stats
    """
    db_source_stats = db.query(SourceStats).order_by(SourceStats.products_count.desc()).all()
    return [convert_source_stat(source) for source in db_source_stats]


@router.get("/brands", response_model=List[str])
async def get_brands(db: Session = Depends(get_db)):
    """
    Get all available brands
    """
    brands = db.query(distinct(Product.brand))\
        .filter(Product.brand.isnot(None))\
        .filter(Product.brand != "")\
        .filter(Product.brand != "na")\
        .all()
    
    return [brand[0] for brand in brands if brand[0]] 