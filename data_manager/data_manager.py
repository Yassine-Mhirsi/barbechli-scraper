import json
import os
from collections import Counter
from typing import Dict, List, Any
from data_manager import db_manager

def load_existing_data():
    """
    Load existing product data from the JSON file
    
    Returns:
        Tuple containing:
        - The complete data structure with stats and products
        - Dictionary of products indexed by uniqueID for easier updates
    """
    # Initialize with empty structure
    existing_data = {"stats": {"total_products": 0, "total_sources": 0, "sources": []}, "products": []}
    
    if os.path.exists("output/barbechli_products_details.json"):
        try:
            with open("output/barbechli_products_details.json", "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            print(f"Loaded {len(existing_data['products'])} existing products")
        except Exception as e:
            print(f"Error loading existing product data: {e}")
    
    # Convert products list to dictionary for efficient lookups
    existing_products_dict = {product["uniqueID"]: product for product in existing_data["products"]}
    
    return existing_data, existing_products_dict

def format_product_data(product_data, product_id):
    """
    Format raw product data into the standardized structure
    
    Args:
        product_data: The raw product data from the API
        product_id: The product ID for reference
    
    Returns:
        Formatted product object
    """
    if not product_data or len(product_data) == 0:
        return None
        
    # We're assuming product_data[0] is the primary data object
    product = product_data[0]
    
    # Create the product object in the desired format
    formatted_product = {
        "uniqueID": product.get("uniqueID", product_id),
        "title": product.get("title", ""),
        "store_label": product.get("store_label", ""),
        "category": product.get("category", ""),
        "subcategory": product.get("subcategory", ""),
        "source_name": product.get("source_name", ""),
        "image": product.get("image", ""),
        "currency": product.get("currency", "TND"),
        "price": product.get("price", 0),
        "price_min": product.get("price_min", 0),
        "price_max": product.get("price_max", 0),
        "price_drop": product.get("price_drop", 0),
        "price_drop_percent": product.get("price_drop_percent", 0),
        "price_week_changed": product.get("price_week_changed", "no"),
        "price_week_drop": product.get("price_week_drop", 0),
        "price_week_drop_percent": product.get("price_week_drop_percent", 0),
        "price_deal": product.get("price_deal", "no"),
        "price_hot_deal": product.get("price_hot_deal", "no"),
        "price_top_deal": product.get("price_top_deal", "no"),
        "link": product.get("link", ""),
        "source_link": product.get("source_link", ""),
        "brand": product.get("brand", "na"),
        "availability": product.get("availability", "unknown"),
        "clicks": product.get("clicks", 0),
        "clicksExternal": product.get("clicksExternal", 0),
        "priceTable": product.get("priceTable", []),
        "availabilityTable": product.get("availabilityTable", []),
        "date_creation": product.get("date_creation", "")
    }
    
    return formatted_product

def update_product(products_dict, product_id, product_data):
    """
    Add or update a product in the products dictionary
    
    Args:
        products_dict: Dictionary of products indexed by uniqueID
        product_id: The product ID being processed
        product_data: The raw product data from the API
    
    Returns:
        True if product was added/updated, False otherwise
    """
    formatted_product = format_product_data(product_data, product_id)
    
    if not formatted_product:
        return False
    
    # Save to database
    success, _, _ = db_manager.add_or_update_product(formatted_product)
    
    if not success:
        print(f"Warning: Failed to save product {product_id} to database")
    
    # Update in-memory dictionary as well (for backward compatibility)
    if product_id in products_dict:
        # Update existing product
        products_dict[product_id].update(formatted_product)
    else:
        # Add new product
        products_dict[product_id] = formatted_product
    
    return True

def calculate_stats(products_dict):
    """
    Calculate statistics based on the current products
    
    Args:
        products_dict: Dictionary of products indexed by uniqueID
    
    Returns:
        Dictionary containing statistics
    """
    products_list = list(products_dict.values())
    
    # Count products by source
    source_counts = Counter(p["source_name"] for p in products_list if "source_name" in p)
    total_products = len(products_list)
    
    sources_stats = []
    for source_name, count in source_counts.items():
        if source_name:  # Skip empty source names
            percentage = (count / total_products) * 100 if total_products > 0 else 0
            sources_stats.append({
                "name": source_name,
                "products": count,
                "percentage": round(percentage, 2)
            })
    
    # Sort sources by product count in descending order
    sources_stats.sort(key=lambda x: x["products"], reverse=True)
    
    return {
        "total_products": total_products,
        "total_sources": len(sources_stats),
        "sources": sources_stats
    }

def save_products_data(products_dict, is_final=False, is_incremental=False):
    """
    Save the current products dictionary to both the database and JSON file
    
    Args:
        products_dict: Dictionary of products indexed by uniqueID
        is_final: Whether this is the final save (for logging)
        is_incremental: Whether this is a quick save after each product
    
    Returns:
        Dictionary containing the saved data structure
    """
    # Convert the dictionary back to a list for the final JSON
    products_list = list(products_dict.values())
    
    # For incremental saves, try to reuse existing stats if available
    if is_incremental and os.path.exists("output/barbechli_products_details.json"):
        try:
            with open("output/barbechli_products_details.json", "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            
            # Update only the products list, keeping existing stats
            existing_data["products"] = products_list
            final_data = existing_data
            
            # Update just the total_products count for accuracy
            final_data["stats"]["total_products"] = len(products_list)
        except Exception:
            # If any errors occur during incremental save, fall back to full save
            is_incremental = False
    
    # For non-incremental saves, recalculate all stats
    if not is_incremental:
        # Calculate stats
        stats = calculate_stats(products_dict)
        
        # Create the final data structure
        final_data = {
            "stats": stats,
            "products": products_list
        }
    
    # Save to JSON file (for backward compatibility)
    with open("output/barbechli_products_details.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    if is_final:
        print(f"All product details saved to output/barbechli_products_details.json")
        print(f"Total products: {final_data['stats']['total_products']}, Total sources: {final_data['stats']['total_sources']}")
        
    elif not is_incremental:
        print(f"Progress saved: total products in file: {final_data['stats']['total_products']}")
    
    return final_data

# Initialize database when module is imported
try:
    db_manager.init_db()
    print("Database initialized successfully")
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")
    print("Continuing with file-based storage only") 