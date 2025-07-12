"""
Demo customer creation script for testing the search functionality.
This script creates some demo customers for testing the search feature.
"""
import os
import sys
import json

# Add the current directory to the path so we can import the checker_app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_demo_customers():
    """Creates demo customers for testing the search functionality."""
    # Demo customers to create
    demo_customers = [
        "Mustermann GmbH",
        "TechCorp AG", 
        "Global Solutions Ltd",
        "Innovations Inc",
        "Deutsche Übersetzung GmbH",
        "International Services",
        "Beispiel AG",
        "Software Solutions GmbH",
        "Marketing Partner",
        "Consulting Group"
    ]
    
    # Create customers directory if it doesn't exist
    customers_dir = "customers"
    if not os.path.exists(customers_dir):
        os.makedirs(customers_dir)
        print(f"Created customers directory: {customers_dir}")
    
    # Create each customer directory
    for customer in demo_customers:
        customer_dir = os.path.join(customers_dir, customer)
        if not os.path.exists(customer_dir):
            os.makedirs(customer_dir)
            print(f"Created customer directory: {customer_dir}")
            
            # Create a simple info file for each customer
            info_file = os.path.join(customer_dir, "customer_info.json")
            customer_info = {
                "name": customer,
                "created": "2025-07-04",
                "projects": [],
                "notes": f"Demo customer: {customer}"
            }
            
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(customer_info, f, indent=2, ensure_ascii=False)
            
            print(f"Created info file: {info_file}")
    
    print(f"\n✅ Successfully created {len(demo_customers)} demo customers!")
    print("You can now test the search functionality in the customer selection dialog.")

if __name__ == "__main__":
    create_demo_customers()
