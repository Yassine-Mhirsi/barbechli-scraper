import threading
import time
import queue
from scrape_product_details import get_product_details
from scrape_ids import collect_ids_thread   


def main():
    """
    Run the product ID collection and product details scraping concurrently
    """    
    # Example parameters for product search
    params = {
        "text": "ordinateur portable",
        "category": "computers",
        "subcategories": "laptops",
        "sources": "tunisianet"
    }
    
    # Create a queue for passing product IDs between threads
    id_queue = queue.Queue()
    
    # Create an event to signal when ID collection is complete
    stop_event = threading.Event()
    
    # Create the ID collector thread
    collector_thread = threading.Thread(
        target=collect_ids_thread,
        args=(id_queue, stop_event, params, 1)
    )
    
    # Create the product details processor thread
    processor_thread = threading.Thread(
        target=get_product_details,
        args=(id_queue, stop_event)
    )
    
    # Start the ID collector thread
    collector_thread.start()
    
    # Give the collector a small head start to find some IDs
    time.sleep(3)
    
    # Start the product details processor thread
    processor_thread.start()
    
    # Wait for both threads to complete
    try:
        # Wait for collector to finish
        collector_thread.join()
        
        # Wait for processor to finish processing all IDs
        processor_thread.join()
        
    except KeyboardInterrupt:
        print("\nInterrupted by user. Stopping threads...")
        stop_event.set()  # Signal threads to stop
        
        # Wait for threads to finish with a timeout
        collector_thread.join(timeout=5)
        processor_thread.join(timeout=5)
        
        print("Scraping process stopped by user")
    
    print("Scraping completed!")


if __name__ == "__main__":
    main() 