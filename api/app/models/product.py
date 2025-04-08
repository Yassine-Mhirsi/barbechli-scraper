from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from app.db.database import Base

class Product(Base):
    """SQLAlchemy model for products table"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(Text, nullable=False)
    store_label = Column(String(255))
    category = Column(String(100))
    subcategory = Column(String(100))
    source_name = Column(String(100), index=True)
    image_url = Column(Text)
    currency = Column(String(10), default="TND")
    current_price = Column(Float)
    brand = Column(String(100))
    availability = Column(String(50))
    link = Column(Text)
    source_link = Column(Text)
    clicks = Column(Integer, default=0)
    clicks_external = Column(Integer, default=0)
    date_creation = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    price_history = Column(JSONB, default=[])
    availability_history = Column(JSONB, default=[])
    additional_data = Column(JSONB, default={})
    
    def __repr__(self):
        return f"<Product {self.unique_id}: {self.title}>"


class SourceStats(Base):
    """SQLAlchemy model for source_stats table"""
    __tablename__ = "source_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    products_count = Column(Integer, default=0)
    percentage = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SourceStats {self.name}: {self.products_count} products>" 