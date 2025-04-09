import uvicorn
import threading
import requests
import time
from datetime import datetime

API_URL = "https://barbechli-api.onrender.com/health"
PING_INTERVAL = 5 * 60  # 1 minute for testing

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

if __name__ == "__main__":
    # Start keep-alive in a separate thread
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    
    # Start the API server
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 