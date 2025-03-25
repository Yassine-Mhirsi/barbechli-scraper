from fastapi import APIRouter

from app.api.v1 import products, stats

api_router = APIRouter()
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(stats.router, prefix="/stats", tags=["statistics"]) 