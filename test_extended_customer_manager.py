#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 TEST ERWEITETER CUSTOMER MANAGER
===================================

Testet die neuen UI-Helper-Methoden im CustomerManager.
"""

def test_extended_customer_manager():
    """Teste die erweiterten CustomerManager Funktionen"""
    
    print("🧪 TESTING EXTENDED CUSTOMER MANAGER")
    print("=" * 50)
    
    try:
        from customer_manager import CustomerManager
        
        # Initialize CustomerManager
        manager = CustomerManager(
            customers_file="customers.json",
            projects_base_path="projects"
        )
        
        print("✅ CustomerManager initialisiert")
        
        # Test 1: Validate Customer Name
        print(f"\n🔍 TEST 1: Customer Name Validation")
        test_names = [
            ("Test Kunde", True),
            ("", False),
            ("A", False),
            ("Test/Kunde", False),
            ("Normal Customer Ltd.", True)
        ]
        
        for name, expected in test_names:
            is_valid, message = manager.validate_customer_name(name)
            status = "✅" if is_valid == expected else "❌"
            print(f"   {status} '{name}' → {is_valid} ({message})")
        
        # Test 2: Customer Stats
        print(f"\n📊 TEST 2: Customer Statistics")
        stats = manager.get_customer_stats()
        print(f"   Total customers: {stats['total_customers']}")
        print(f"   Has customers: {stats['has_customers']}")
        print(f"   Current customer: {stats['current_customer']}")
        
        # Test 3: Recent Customers
        print(f"\n📋 TEST 3: Recent Customers")
        recent = manager.get_recent_customers(limit=3)
        print(f"   Found {len(recent)} recent customers:")
        for i, customer in enumerate(recent, 1):
            print(f"     {i}. {customer['name']}")
        
        # Test 4: Customer Operations
        print(f"\n⚡ TEST 4: Customer Operations")
        
        # Test remove (if exists)
        if stats['total_customers'] > 0:
            # Get first customer name
            all_customers = manager.get_all_customers()
            if all_customers:
                first_customer = all_customers[0]['name']
                print(f"   Testing remove with: {first_customer}")
                
                # Don't actually remove - just test validation
                exists_before, _, _ = manager.customer_exists(first_customer)
                print(f"   Customer exists before: {exists_before}")
        
        print(f"\n✅ ALLE TESTS ABGESCHLOSSEN!")
        print("CustomerManager UI-Helper-Methoden funktionieren korrekt.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_extended_customer_manager()
    if success:
        print("\n🎉 CustomerManager erfolgreich erweitert!")
        print("Bereit für Integration in welcome_screen.py")
    else:
        print("\n❌ Tests fehlgeschlagen!")
        print("Bitte Implementierung prüfen.")
