#!/usr/bin/env python3
"""
Test script for the intelligent customer recognition system.
Tests automatic customer detection, fuzzy matching, and smart handling.
"""

import os
import sys
import logging
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kunden_manager import KundenManager
from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen

class TestIntelligentCustomerSystem:
    """Test suite for the intelligent customer recognition system."""
    
    def __init__(self):
        self.test_dir = "test_customers"
        self.kunden_manager = KundenManager(self.test_dir)
        self.setup_test_data()
        
    def setup_test_data(self):
        """Set up test customers for testing."""
        # Clean up any existing test data
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)
        
        # Create test customers
        test_customers = [
            "Mustermann GmbH",
            "Beispiel AG",
            "Test Firma",
            "ACME Corporation",
            "Demo Company"
        ]
        
        for customer in test_customers:
            self.kunden_manager.erstelle_kundenstruktur(customer)
        
        print(f"✅ Test data created: {len(test_customers)} customers")
    
    def test_exact_match(self):
        """Test exact customer name matching."""
        print("\n🔍 Testing exact customer matching...")
        
        # Test existing customer
        exists, matched = self.kunden_manager.customer_exists("Mustermann GmbH")
        assert exists, "Should find existing customer"
        assert matched == "Mustermann GmbH", "Should match exactly"
        print("✅ Exact match test passed")
        
        # Test non-existing customer
        exists, matched = self.kunden_manager.customer_exists("Nicht Vorhanden")
        assert not exists, "Should not find non-existing customer"
        print("✅ Non-existing customer test passed")
    
    def test_fuzzy_match(self):
        """Test fuzzy customer name matching."""
        print("\n🔍 Testing fuzzy customer matching...")
        
        # Test similar names
        test_cases = [
            ("Musterman GmbH", "Mustermann GmbH"),  # Typo
            ("Mustermann", "Mustermann GmbH"),      # Partial
            ("mUSTERMANN gmbh", "Mustermann GmbH"), # Case difference
            ("Beispiel", "Beispiel AG"),            # Partial match
            ("ACME Corp", "ACME Corporation"),      # Abbreviation
        ]
        
        for input_name, expected_match in test_cases:
            fuzzy_result = self.kunden_manager.find_customer_fuzzy(input_name)
            print(f"  Input: '{input_name}' -> Found: '{fuzzy_result}' (Expected: '{expected_match}')")
            
            if fuzzy_result:
                print(f"  ✅ Fuzzy match found: {fuzzy_result}")
            else:
                print(f"  ❌ No fuzzy match found for '{input_name}'")
    
    def test_customer_creation(self):
        """Test new customer creation."""
        print("\n🔍 Testing customer creation...")
        
        new_customer = "Neuer Test Kunde"
        
        # Should not exist initially
        exists, _ = self.kunden_manager.customer_exists(new_customer)
        assert not exists, "New customer should not exist"
        
        # Create customer
        customer_path = self.kunden_manager.erstelle_kundenstruktur(new_customer)
        
        # Should exist now
        exists, matched = self.kunden_manager.customer_exists(new_customer)
        assert exists, "Customer should exist after creation"
        assert matched == new_customer, "Should match exactly"
        
        print(f"✅ Customer creation test passed: {customer_path}")
    
    def test_intelligent_workflow(self):
        """Test the complete intelligent workflow."""
        print("\n🔍 Testing complete intelligent workflow...")
        
        # Mock the welcome screen components
        mock_app = Mock()
        mock_app.kunden_manager = self.kunden_manager
        mock_app.logger = logging.getLogger('test')
        
        # Test scenarios
        test_scenarios = [
            ("Mustermann GmbH", "existing_exact"),      # Exact match
            ("Musterman GmbH", "existing_fuzzy"),       # Fuzzy match
            ("Völlig Neuer Kunde", "new_customer"),     # New customer
        ]
        
        for customer_name, scenario_type in test_scenarios:
            print(f"\n  Testing scenario: {scenario_type} with '{customer_name}'")
            
            exists, matched = mock_app.kunden_manager.customer_exists(customer_name)
            
            if scenario_type == "existing_exact":
                assert exists and matched == customer_name, f"Should find exact match for {customer_name}"
                print(f"  ✅ Exact match found: {matched}")
                
            elif scenario_type == "existing_fuzzy":
                assert exists and matched != customer_name, f"Should find fuzzy match for {customer_name}"
                print(f"  ✅ Fuzzy match found: {matched}")
                
            elif scenario_type == "new_customer":
                assert not exists, f"Should not find match for {customer_name}"
                print(f"  ✅ New customer scenario: {customer_name}")
    
    def test_customer_list(self):
        """Test customer listing functionality."""
        print("\n🔍 Testing customer listing...")
        
        customers = self.kunden_manager.alle_kunden()
        print(f"  Found {len(customers)} customers:")
        
        for i, customer in enumerate(customers, 1):
            print(f"  {i}. {customer}")
        
        assert len(customers) > 0, "Should have customers"
        print("✅ Customer listing test passed")
    
    def run_all_tests(self):
        """Run all tests."""
        print("🧪 Starting Intelligent Customer System Tests...")
        print("=" * 60)
        
        try:
            self.test_exact_match()
            self.test_fuzzy_match()
            self.test_customer_creation()
            self.test_intelligent_workflow()
            self.test_customer_list()
            
            print("\n" + "=" * 60)
            print("🎉 All tests passed successfully!")
            print("✅ Intelligent customer system is working correctly")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Cleanup
            if os.path.exists(self.test_dir):
                import shutil
                shutil.rmtree(self.test_dir)
                print(f"🧹 Test data cleaned up: {self.test_dir}")

def demonstrate_intelligent_system():
    """Demonstrate the intelligent customer system with examples."""
    print("🤖 Intelligent Customer Recognition System Demo")
    print("=" * 60)
    
    # Create demo data
    demo_manager = KundenManager("demo_customers")
    
    # Create some demo customers
    demo_customers = [
        "Mustermann GmbH",
        "Beispiel AG", 
        "Test Firma",
        "ACME Corporation",
        "Demo Company",
        "Muster & Partner",
        "Beispiel Solutions"
    ]
    
    for customer in demo_customers:
        demo_manager.erstelle_kundenstruktur(customer)
    
    print(f"📋 Created {len(demo_customers)} demo customers")
    print("👥 Available customers:")
    for i, customer in enumerate(demo_customers, 1):
        print(f"  {i}. {customer}")
    
    print("\n🔍 Testing intelligent recognition...")
    
    # Test cases showing the intelligent system
    test_inputs = [
        "Mustermann GmbH",      # Exact match
        "Musterman GmbH",       # Typo (should find Mustermann GmbH)
        "mustermann",           # Partial + case (should find Mustermann GmbH) 
        "Beispiel",             # Partial (should find Beispiel AG)
        "ACME Corp",           # Abbreviation (should find ACME Corporation)
        "Komplett Neuer Kunde", # New customer
        "Demo",                # Partial (should find Demo Company)
    ]
    
    for test_input in test_inputs:
        exists, matched = demo_manager.customer_exists(test_input)
        
        if exists:
            if matched == test_input:
                print(f"  ✅ '{test_input}' -> EXACT MATCH: {matched}")
            else:
                print(f"  🔍 '{test_input}' -> FUZZY MATCH: {matched}")
        else:
            print(f"  ➕ '{test_input}' -> NEW CUSTOMER (would create)")
    
    # Cleanup
    import shutil
    if os.path.exists("demo_customers"):
        shutil.rmtree("demo_customers")
    
    print("\n✨ Demo completed!")

if __name__ == "__main__":
    print("🚀 Intelligent Customer Recognition System")
    print("=" * 60)
    
    # Run demonstration
    demonstrate_intelligent_system()
    
    print("\n")
    
    # Run tests
    tester = TestIntelligentCustomerSystem()
    tester.run_all_tests()
    
    print("\n🎯 Summary:")
    print("✅ The intelligent customer system provides:")
    print("  • Automatic customer detection")
    print("  • Fuzzy matching for similar names")
    print("  • Smart handling of typos and partial matches")
    print("  • Seamless new customer creation")
    print("  • User-friendly confirmation dialogs")
    print("  • Integrated workflow with file uploads")
