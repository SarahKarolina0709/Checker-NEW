#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 DEBUG CUSTOMER EXISTENCE PROBLEM
===================================

Debuggt warum die Kunde-bereits-existiert-Warnung nicht funktioniert.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from pathlib import Path

def debug_customer_data():
    """Debug der Kundendaten-Struktur"""
    print("🔍 DEBUGGING CUSTOMER EXISTENCE PROBLEM")
    print("=" * 50)
    
    # Prüfe customers.json
    customers_file = "customers.json"
    print(f"\n📁 Checking {customers_file}...")
    
    if os.path.exists(customers_file):
        try:
            with open(customers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✅ File exists and is valid JSON")
            print(f"📊 Data type: {type(data)}")
            print(f"📊 Data length: {len(data) if isinstance(data, (list, dict)) else 'N/A'}")
            
            if isinstance(data, list):
                print(f"📋 Customer list (first 5):")
                for i, customer in enumerate(data[:5]):
                    print(f"   {i+1}. {customer} (type: {type(customer)})")
                    if isinstance(customer, dict):
                        print(f"      Name: {customer.get('name', 'NO NAME')}")
            elif isinstance(data, dict):
                print(f"📋 Customer dict keys: {list(data.keys())}")
                if 'customers' in data:
                    customers = data['customers']
                    print(f"📋 Customers list (first 5):")
                    for i, customer in enumerate(customers[:5]):
                        print(f"   {i+1}. {customer} (type: {type(customer)})")
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    else:
        print(f"❌ File does not exist")
    
    # Teste Existenz-Prüfung-Logik
    print(f"\n🧪 Testing existence check logic...")
    
    # Simuliere verschiedene Datenstrukturen
    test_data_sets = [
        (["Müller GmbH", "Schmidt & Co"], "string list"),
        ([{"name": "Müller GmbH"}, {"name": "Schmidt & Co"}], "dict list"),
        ({"customers": ["Müller GmbH", "Schmidt & Co"]}, "wrapped dict"),
    ]
    
    test_names = ["Müller GmbH", "müller gmbh", "Schmidt & Co", "Neuer Kunde"]
    
    for customers_data, data_type in test_data_sets:
        print(f"\n📊 Testing with {data_type}:")
        for test_name in test_names:
            exists = simulate_exists_check(test_name, customers_data)
            print(f"   '{test_name}' → {'EXISTS' if exists else 'NEW'}")

def simulate_exists_check(customer_name, customers_data):
    """Simuliert die _customer_exists Logik"""
    # Handle wrapped dict format
    if isinstance(customers_data, dict) and 'customers' in customers_data:
        customers_data = customers_data['customers']
    
    for customer in customers_data:
        existing_name = customer if isinstance(customer, str) else customer.get('name', '')
        if existing_name and existing_name.lower() == customer_name.lower():
            return True
    return False

def debug_live_customer_module():
    """Debug des Live Customer Modules"""
    print(f"\n🔧 DEBUGGING LIVE CUSTOMER MODULE")
    print("=" * 50)
    
    try:
        # Import customer module
        from welcome_screen_customer import WelcomeScreenCustomer
        from customer_manager import CustomerManager
        
        print("✅ Imports successful")
        
        # Mock parent
        class MockParent:
            def __init__(self):
                self.projects_base_path = "test_projects"
                self.messages = []
            def show_toast(self, msg, type="info", duration=3000):
                self.messages.append((msg, type))
                print(f"📢 TOAST ({type}): {msg}")
            def get_color(self, name): return "#000000"
            def get_font(self, name): return ('Segoe UI', 12, 'normal')
            def get_spacing(self, name): return 8
        
        mock_parent = MockParent()
        customer_module = WelcomeScreenCustomer(mock_parent)
        
        print(f"✅ Customer module initialized")
        print(f"📊 Customer manager available: {hasattr(customer_module, 'customer_manager') and customer_module.customer_manager is not None}")
        print(f"📊 Customers data: {len(customer_module.customers_data)} items")
        print(f"📊 Customers data type: {type(customer_module.customers_data)}")
        
        if customer_module.customers_data:
            print(f"📋 First few customers:")
            for i, customer in enumerate(customer_module.customers_data[:3]):
                name = customer if isinstance(customer, str) else customer.get('name', 'NO NAME')
                print(f"   {i+1}. {name} (type: {type(customer)})")
        
        # Test existence check
        if customer_module.customers_data:
            first_customer = customer_module.customers_data[0]
            first_name = first_customer if isinstance(first_customer, str) else first_customer.get('name', '')
            if first_name:
                print(f"\n🧪 Testing existence check with '{first_name}':")
                exists = customer_module._customer_exists(first_name)
                print(f"   Result: {'EXISTS' if exists else 'NEW'}")
                
                # Test case insensitive
                exists_lower = customer_module._customer_exists(first_name.lower())
                print(f"   Lowercase test: {'EXISTS' if exists_lower else 'NEW'}")
        
    except Exception as e:
        print(f"❌ Error in live debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_customer_data()
    debug_live_customer_module()
    
    print("\n" + "=" * 50)
    print("🎯 DEBUGGING CHECKLIST:")
    print("1. Is customers.json loading correctly?")
    print("2. Is customers_data populated?")
    print("3. Is _customer_exists logic working?")
    print("4. Is customer_manager available?")
    print("5. Are toast messages being triggered?")
