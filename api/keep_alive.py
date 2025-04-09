import requests
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_URL = "https://barbechli-api.onrender.com"
PING_INTERVAL = 60  # 1 minute for testing

def ping_api():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            logger.info(f"Successfully pinged API at {datetime.now()}")
        else:
            logger.warning(f"API ping returned status code {response.status_code}")
    except Exception as e:
        logger.error(f"Error pinging API: {e}")

def main():
    logger.info("Starting keep-alive service...")
    while True:
        ping_api()
        time.sleep(PING_INTERVAL)

if __name__ == "__main__":
    main() 