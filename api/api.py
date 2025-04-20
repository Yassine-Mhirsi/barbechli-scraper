import datetime
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# Database URL (Replace with your Neon PostgreSQL connection string)
DATABASE_URL = "postgresql://neondb_owner:npg_OZ9myoVwL8nb@ep-morning-glitter-a2z9vqaa-pooler.eu-central-1.aws.neon.tech/barbechli-scraper?sslmode=require"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a SessionLocal instance
db = SessionLocal()

# Initialize FastAPI app
app = FastAPI()

# SQLAlchemy Base
Base = declarative_base()

# Define a model (example: a table named 'items')
class Item(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)

# Pydantic model for response
class ItemResponse(BaseModel):
    id: int
    product_id: str
    price : int
    date: datetime
    product: str

    class Config:
        from_attributes = True

# Create tables in the database (if they don't exist)
Base.metadata.create_all(bind=engine)

# HTTP GET method to fetch all items
@app.get("/items/", response_model=list[ItemResponse])
def get_items():
    items = db.query(Item).all()
    if not items:
        raise HTTPException(status_code=404, detail="No items found")
    return items

# HTTP GET method to fetch a single item by ID
@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item