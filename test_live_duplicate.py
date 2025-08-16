#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 LIVE CUSTOMER DUPLICATE TEST
===============================

Testet die Live-Duplikat-Erkennung im Welcome Screen.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import json
from pathlib import Path

# Import the welcome screen customer module
try:
    from welcome_screen_customer import WelcomeScreenCustomer
    from customer_manager import CustomerManager
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    IMPORTS_OK = False

class MockParent:
    """Mock parent für isoliertes Testen"""
    def __init__(self):
        self.projects_base_path = "test_projects"
        self.toast_messages = []
        
    def show_toast(self, message, toast_type="info", duration=3000):
        """Mock toast für Test-Logging"""
        self.toast_messages.append({
            'message': message,
            'type': toast_type,
            'timestamp': time.time()
        })
        print(f"📢 TOAST ({toast_type}): {message}")
        
    def get_color(self, color_name):
        """Mock Farben"""
        colors = {
            'surface': '#FFFFFF',
            'surface_border': '#E5E7EB',
            'gray_700': '#374151',
            'gray_500': '#6B7280',
            'primary': '#1F4E79',
            'success': '#2E8B57',
            'warning': '#F2994A'
        }
        return colors.get(color_name, '#000000')
        
    def get_font(self, font_name):
        """Mock Fonts"""
        return ('Segoe UI', 12, 'normal')
        
    def get_spacing(self, spacing_name):
        """Mock Spacing"""
        return 8

def test_duplicate_detection_live():
    """Live-Test der Duplikat-Erkennung"""
    if not IMPORTS_OK:
        print("❌ Cannot run live test - imports failed")
        return
        
    print("🧪 LIVE CUSTOMER DUPLICATE DETECTION TEST")
    print("=" * 50)
    
    # Mock parent erstellen
    mock_parent = MockParent()
    
    # Customer Module initialisieren
    customer_module = WelcomeScreenCustomer(mock_parent)
    
    # Test-Kunden hinzufügen
    print("\n1️⃣ Adding first customer 'TestCorp'...")
    customer_module.customer_entry = MockEntry("TestCorp")
    customer_module._add_customer_working()
    
    print(f"📊 Toast messages so far: {len(mock_parent.toast_messages)}")
    for msg in mock_parent.toast_messages:
        print(f"   {msg['type']}: {msg['message']}")
    
    # Versuche denselben Kunden nochmal hinzuzufügen
    print("\n2️⃣ Trying to add 'TestCorp' again (should warn)...")
    mock_parent.toast_messages.clear()
    customer_module.customer_entry = MockEntry("TestCorp")
    customer_module._add_customer_working()
    
    print(f"📊 Toast messages after duplicate attempt: {len(mock_parent.toast_messages)}")
    for msg in mock_parent.toast_messages:
        print(f"   {msg['type']}: {msg['message']}")
    
    # Teste Case-Insensitive
    print("\n3️⃣ Trying to add 'testcorp' (lowercase, should warn)...")
    mock_parent.toast_messages.clear()
    customer_module.customer_entry = MockEntry("testcorp")
    customer_module._add_customer_working()
    
    print(f"📊 Toast messages after case test: {len(mock_parent.toast_messages)}")
    for msg in mock_parent.toast_messages:
        print(f"   {msg['type']}: {msg['message']}")
    
    # Teste neuen Kunden
    print("\n4️⃣ Adding genuinely new customer 'NewCorp'...")
    mock_parent.toast_messages.clear()
    customer_module.customer_entry = MockEntry("NewCorp")
    customer_module._add_customer_working()
    
    print(f"📊 Toast messages after new customer: {len(mock_parent.toast_messages)}")
    for msg in mock_parent.toast_messages:
        print(f"   {msg['type']}: {msg['message']}")
        
    print(f"\n✅ Final customer count: {len(customer_module.customers_data)}")
    print("📋 Final customer list:")
    for i, customer in enumerate(customer_module.customers_data, 1):
        name = customer if isinstance(customer, str) else customer.get('name', 'Unknown')
        print(f"   {i}. {name}")

class MockEntry:
    """Mock Entry Widget für Tests"""
    def __init__(self, text=""):
        self.text = text
        
    def get(self):
        return self.text
        
    def delete(self, start, end):
        pass
        
    def insert(self, pos, text):
        self.text = text

if __name__ == "__main__":
    test_duplicate_detection_live()
    
    print("\n" + "=" * 50)
    print("🎯 EXPECTED BEHAVIOR SUMMARY:")
    print("✅ First 'TestCorp' → Success toast")
    print("⚠️  Second 'TestCorp' → Warning toast + auto-select")
    print("⚠️  'testcorp' (case) → Warning toast + auto-select") 
    print("✅ 'NewCorp' → Success toast")
    print("📊 Final count: 2 unique customers")
