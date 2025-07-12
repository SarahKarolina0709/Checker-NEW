#!/usr/bin/env python3
"""
Test script to create demo customers and test search functionality.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kunden_manager import KundenManager

def create_demo_customers():
    """Create some demo customers for testing search functionality."""
    try:
        kunden_manager = KundenManager()
        
        demo_customers = [
            "Test GmbH",
            "Mustermann AG", 
            "Beispiel Firma",
            "Demo Corporation",
            "Sample Business",
            "Testkunde 123",
            "ABC Company",
            "XYZ Solutions"
        ]
        
        for customer in demo_customers:
            try:
                if not kunden_manager.customer_exists(customer):
                    kunden_manager.neuer_kunde(customer)
                    print(f"✓ Created customer: {customer}")
                else:
                    print(f"- Customer already exists: {customer}")
            except Exception as e:
                print(f"✗ Error creating customer {customer}: {e}")
        
        print(f"\nTotal customers: {len(kunden_manager.alle_kunden())}")
        print("Demo customers created successfully!")
        
    except Exception as e:
        print(f"Error creating demo customers: {e}")

if __name__ == "__main__":
    create_demo_customers()
