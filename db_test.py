#!/usr/bin/env python
"""
Test script for the database functionality.
This script verifies that the database connection and operations work correctly.
"""

import db_manager
import time
import uuid
import random

def test_connection():
    """Test database connection and initialization"""
    print("\n=== Testing Database Connection ===")
    success = db_manager.init_db()
    if success:
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
    return success

def test_add_product():
    """Test adding a product to the database"""
    print("\n=== Testing Product Addition ===")
    
    # Create a test product
    unique_id = f"test-{uuid.uuid4()}"
    product = {
        "uniqueID": unique_id,
        "title": "Test Product",
        "store_label": "Test Store",
        "category": "test",
        "subcategory": "unit_test",
        "source_name": "test_script",
        "image": "https://example.com/image.jpg",
        "currency": "TND",
        "price": 100.0,
        "price_min": 90.0,
        "price_max": 110.0,
        "availability": "on_stock",
        "link": "https://example.com/product",
        "source_link": "https://example.com",
        "brand": "Test Brand",
        "clicks": 0,
        "clicksExternal": 0
    }
    
    # Add product
    success, product_id, is_new = db_manager.add_or_update_product(product)
    
    if success and is_new:
        print(f"✅ Product added successfully (ID: {product_id})")
    else:
        print("❌ Failed to add product")
    
    return success, product, product_id

def test_update_product(product, product_id):
    """Test updating a product"""
    print("\n=== Testing Product Update ===")
    
    # Modify the product
    product["price"] = 105.0
    product["availability"] = "limited_stock"
    
    # Update product
    success, updated_id, is_new = db_manager.add_or_update_product(product)
    
    if success and not is_new and updated_id == product_id:
        print("✅ Product updated successfully")
    else:
        print("❌ Failed to update product")
    
    return success

def test_get_products():
    """Test getting all products"""
    print("\n=== Testing Product Retrieval ===")
    
    products = db_manager.get_all_products()
    
    if products:
        print(f"✅ Retrieved {len(products)} products")
    else:
        print("❌ Failed to retrieve products or no products exist")
    
    return len(products) > 0

def test_source_stats():
    """Test source statistics"""
    print("\n=== Testing Source Statistics ===")
    
    stats = db_manager.get_source_stats()
    
    if stats:
        print(f"✅ Retrieved stats for {len(stats)} sources")
        for source in stats:
            print(f"  - {source['name']}: {source['products_count']} products ({source['percentage']}%)")
    else:
        print("❌ Failed to retrieve source statistics or no sources exist")
    
    return len(stats) > 0

def main():
    """Run all tests"""
    print("Starting database tests...\n")
    
    # Test connection
    if not test_connection():
        print("\n❌ Connection test failed. Aborting remaining tests.")
        return False
    
    # Test adding a product
    success, product, product_id = test_add_product()
    if not success:
        print("\n❌ Add product test failed. Aborting remaining tests.")
        return False
    
    # Test updating a product
    if not test_update_product(product, product_id):
        print("\n❌ Update product test failed. Aborting remaining tests.")
        return False
    
    # Test getting products
    test_get_products()
    
    # Test source stats
    test_source_stats()
        
    # Clean up
    db_manager.close_all_connections()
    
    print("\nAll tests completed!")
    return True

if __name__ == "__main__":
    main() 