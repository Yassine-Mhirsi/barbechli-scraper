import threading
import time
import queue
from scrape_product_details import get_product_details
from scrape_ids import collect_ids_thread   


def main():
    # Example parameters for product search
    params = {
        "text": "kit de reparation",
        # "category": "computers",
        # "subcategories": "laptops",
        # "sources": "tunisianet"
    }
    
    # Create a queue for passing IDs between threads
    id_queue = queue.Queue()
    # Event to signal when ID collection is complete
    stop_event = threading.Event()
    
    # Create and start the ID collector thread
    collector_thread = threading.Thread(
        target=collect_ids_thread,
        args=(id_queue, stop_event, params, 1)
    )
    collector_thread.start()
    
    
    # Start processing IDs from the queue
    product_details = get_product_details(id_queue, stop_event)
    
    # Wait for the collector to finish
    collector_thread.join()
    
    print("\nScraping completed!")

if __name__ == "__main__":
    main() 