from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
import requests
import time
from datetime import datetime

from app.api.v1 import api_router
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["status"])
async def root():
    """
    Root endpoint to check if the API is running
    """
    return {
        "message": "Welcome to Barbechli API",
        "status": "online",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["status"])
async def health():
    """
    Health check endpoint
    """
    return {"status": "healthy"}


# Keep-alive mechanism
API_URL = "https://barbechli-api.onrender.com/"
PING_INTERVAL = 14 *60  # 14 minutes (Render's free tier has a 15-minute timeout)

def ping_api():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            print(f"Successfully pinged API at {datetime.now()}")
        else:
            print(f"API ping returned status code {response.status_code}")
    except Exception as e:
        print(f"Error pinging API: {e}")

def keep_alive():
    print("Starting keep-alive service...")
    while True:
        ping_api()
        time.sleep(PING_INTERVAL)

# Start keep-alive in a separate thread
keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
keep_alive_thread.start()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 