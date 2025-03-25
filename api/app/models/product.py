from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
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
    additional_data = Column(JSONB, default={})
    
    # Relationships
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    availability_history = relationship("AvailabilityHistory", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product {self.unique_id}: {self.title}>"


class PriceHistory(Base):
    """SQLAlchemy model for price_history table"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="price_history")
    
    def __repr__(self):
        return f"<PriceHistory {self.product_id}: {self.price} at {self.recorded_at}>"


class AvailabilityHistory(Base):
    """SQLAlchemy model for availability_history table"""
    __tablename__ = "availability_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    availability = Column(String(50), nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="availability_history")
    
    def __repr__(self):
        return f"<AvailabilityHistory {self.product_id}: {self.availability} at {self.recorded_at}>"


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