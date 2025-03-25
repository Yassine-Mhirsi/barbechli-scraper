from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

from app.core.config import settings


class PriceHistoryItem(BaseModel):
    """Price history item schema"""
    date_price: datetime
    price: float
    
    class Config:
        orm_mode = True


class AvailabilityHistoryItem(BaseModel):
    """Availability history item schema"""
    date_availability: datetime
    availability: str
    
    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    """Base schema for product attributes"""
    title: str
    store_label: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    source_name: Optional[str] = None
    image: Optional[str] = None
    currency: str = "TND"
    price: float
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    price_drop: Optional[float] = 0
    price_drop_percent: Optional[float] = 0
    price_week_changed: Optional[str] = "no"
    price_week_drop: Optional[float] = 0
    price_week_drop_percent: Optional[float] = 0
    price_deal: Optional[str] = "no"
    price_hot_deal: Optional[str] = "no"
    price_top_deal: Optional[str] = "no"
    brand: Optional[str] = None
    availability: Optional[str] = "unknown"
    link: Optional[str] = None
    source_link: Optional[str] = None
    clicks: Optional[int] = 0
    clicksExternal: Optional[int] = 0


class ProductCreate(ProductBase):
    """Schema for creating a product"""
    uniqueID: str


class ProductInDB(ProductBase):
    """Schema for product stored in database"""
    uniqueID: str
    date_creation: datetime
    last_updated: datetime
    priceTable: List[PriceHistoryItem] = []
    availabilityTable: List[AvailabilityHistoryItem] = []
    
    class Config:
        orm_mode = True


class Product(ProductInDB):
    """Schema for product response"""
    pass


class ProductList(BaseModel):
    """Schema for list of products"""
    total: int
    items: List[Product]


class SourceStatBase(BaseModel):
    """Base schema for source statistics"""
    name: str
    products: int
    percentage: float


class SourceStat(SourceStatBase):
    """Schema for source statistics response"""
    class Config:
        orm_mode = True


class StatsResponse(BaseModel):
    """Schema for statistics response"""
    total_products: int
    total_sources: int
    sources: List[SourceStat]


class ProductSearchParams(BaseModel):
    """Schema for product search/filter parameters"""
    q: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    source_name: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    availability: Optional[str] = None
    sort_by: Optional[str] = "last_updated"
    sort_order: Optional[str] = "desc"
    skip: int = Field(0, ge=0)
    limit: int = Field(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE) 