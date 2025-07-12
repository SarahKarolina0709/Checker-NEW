#!/usr/bin/env python3
"""
Test script to verify search functionality logic.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kunden_manager import KundenManager

def test_search_logic():
    """Test the search filtering logic."""
    try:
        kunden_manager = KundenManager()
        all_customers = kunden_manager.alle_kunden()
        
        print(f"Total customers: {len(all_customers)}")
        print("All customers:")
        for i, customer in enumerate(all_customers, 1):
            print(f"  {i}. {customer}")
        
        # Test search functionality
        search_terms = ["test", "gmbh", "ag", "firma", "demo"]
        
        for search_term in search_terms:
            print(f"\n🔍 Search for '{search_term}':")
            filtered_customers = [
                customer for customer in all_customers 
                if search_term.lower() in customer.lower()
            ]
            
            if filtered_customers:
                for customer in filtered_customers:
                    print(f"  ✓ {customer}")
            else:
                print(f"  No results for '{search_term}'")
        
    except Exception as e:
        print(f"Error testing search logic: {e}")

if __name__ == "__main__":
    test_search_logic()
