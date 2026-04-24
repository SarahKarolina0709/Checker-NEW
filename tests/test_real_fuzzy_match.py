#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 REAL FUZZY MATCH UI TEST
Test ob der Fuzzy Match Dialog in der echten GUI aufgerufen wird
"""

def test_real_customer_data():
    """Test mit echten Kundendaten"""
    print("🎯 REAL CUSTOMER DATA FUZZY TEST")
    print("=" * 50)
    
    try:
        with open('customers.json', 'r', encoding='utf-8') as f:
            customers = f.read()
            print(f"📋 Customers.json content:\n{customers}\n")
    except Exception as e:
        print(f"⚠️ Could not read customers.json: {e}")
    
    try:
        from customer_manager import CustomerManager
        manager = CustomerManager()
        
        # Get actual customer names
        actual_customers = []
        for customer in manager.customers_data:
            if isinstance(customer, dict) and 'name' in customer:
                actual_customers.append(customer['name'])
            elif isinstance(customer, str):
                actual_customers.append(customer)
        
        print(f"📋 ACTUAL CUSTOMERS IN SYSTEM:")
        for i, customer in enumerate(actual_customers, 1):
            print(f"   {i}. '{customer}'")
        
        if not actual_customers:
            print("❌ NO CUSTOMERS FOUND - Cannot test fuzzy match")
            return False
        
        # Test fuzzy variations of real customers
        test_cases = []
        for customer in actual_customers[:3]:  # Test first 3 customers
            if len(customer) > 1:
                # Create fuzzy variations
                variations = [
                    customer[:-1],  # Remove last character
                    customer[:-2] if len(customer) > 2 else customer[:-1],  # Remove last 2 chars
                    customer.replace('e', 'a') if 'e' in customer else customer + 'x',  # Character substitution
                    customer.lower() if customer.isupper() else customer.upper()  # Case change
                ]
                test_cases.extend([(var, customer) for var in variations if var != customer])
        
        print(f"\n🧪 TESTING FUZZY VARIATIONS:")
        
        found_fuzzy_matches = []
        
        for variation, original in test_cases[:5]:  # Test first 5 cases
            print(f"\n   Testing '{variation}' (should match '{original}'):")
            
            # Test with CustomerManager
            success, message, similar_customers = manager.add_customer(variation)
            
            if not success and similar_customers:
                print(f"   ✅ FUZZY MATCH FOUND!")
                print(f"      Similar customers: {similar_customers}")
                found_fuzzy_matches.append((variation, similar_customers))
            elif success:
                print(f"   ⚠️ Customer was added (no fuzzy match triggered)")
            else:
                print(f"   ❌ No similar customers found")
        
        print(f"\n🎯 FUZZY MATCH RESULTS:")
        if found_fuzzy_matches:
            print(f"   Found {len(found_fuzzy_matches)} fuzzy matches that should trigger dialog:")
            for variation, similar in found_fuzzy_matches:
                print(f"   • '{variation}' → {similar}")
            return True
        else:
            print(f"   ❌ No fuzzy matches found with real customer data")
            return False
    
    except Exception as e:
        print(f"❌ Real data test error: {e}")
        return False

def create_test_customers():
    """Create test customers for fuzzy matching"""
    print(f"\n🔧 CREATING TEST CUSTOMERS FOR FUZZY MATCH")
    print("=" * 50)
    
    import json
    
    test_customers = [
        "Tesla Motors",
        "Google Inc", 
        "Microsoft Corp",
        "Apple Computer",
        "Amazon Web Services"
    ]
    
    try:
        # Read existing customers
        try:
            with open('customers.json', 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except:
            existing = []
        
        # Add test customers if not already present
        customers_added = []
        for test_customer in test_customers:
            # Check if already exists
            exists = False
            for customer in existing:
                name = customer.get('name', str(customer)) if isinstance(customer, dict) else str(customer)
                if name == test_customer:
                    exists = True
                    break
            
            if not exists:
                existing.append({"name": test_customer})
                customers_added.append(test_customer)
        
        if customers_added:
            # Save updated customers
            with open('customers.json', 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Added {len(customers_added)} test customers:")
            for customer in customers_added:
                print(f"   • {customer}")
        else:
            print(f"✅ Test customers already exist")
        
        return True
        
    except Exception as e:
        print(f"❌ Create test customers error: {e}")
        return False

def test_fuzzy_variations():
    """Test specific fuzzy variations that should work"""
    print(f"\n🧪 SPECIFIC FUZZY VARIATIONS TEST")
    print("=" * 50)
    
    try:
        from customer_manager import CustomerManager
        manager = CustomerManager()
        
        # Test cases that should definitely trigger fuzzy match
        test_variations = [
            ("Googl", "Google Inc"),  # Missing last character
            ("Microsft", "Microsoft Corp"),  # Typo
            ("Appl", "Apple Computer"),  # Shortened
            ("tesla", "Tesla Motors"),  # Case difference
            ("amazn", "Amazon Web Services")  # Missing vowel
        ]
        
        fuzzy_triggers = []
        
        for variation, expected_match in test_variations:
            print(f"\n   🧪 Testing '{variation}':")
            
            # First check if expected customer exists
            found_expected = False
            for customer in manager.customers_data:
                name = customer.get('name', str(customer)) if isinstance(customer, dict) else str(customer)
                if expected_match.lower() in name.lower():
                    found_expected = True
                    break
            
            if not found_expected:
                print(f"      ⚠️ Expected customer '{expected_match}' not found in system")
                continue
            
            # Test fuzzy match
            success, message, similar_customers = manager.add_customer(variation)
            
            if not success and similar_customers:
                print(f"      ✅ FUZZY MATCH TRIGGERED!")
                print(f"         Message: {message}")
                print(f"         Similar: {similar_customers}")
                fuzzy_triggers.append((variation, similar_customers))
            elif success:
                print(f"      ⚠️ Customer added without fuzzy check")
            else:
                print(f"      ❌ No fuzzy match found")
        
        print(f"\n🎯 FUZZY TRIGGER SUMMARY:")
        if fuzzy_triggers:
            print(f"   ✅ Found {len(fuzzy_triggers)} cases that trigger fuzzy dialog:")
            for variation, similar in fuzzy_triggers:
                print(f"      • '{variation}' triggers dialog with {len(similar)} similar customers")
            
            # Show what _add_customer should do
            print(f"\n🎨 GUI INTEGRATION:")
            print(f"   → _add_customer should call _show_duplicate_warning_dialog")
            print(f"   → Dialog should show customer options")
            print(f"   → User should be able to select similar customer")
            
            return True
        else:
            print(f"   ❌ No fuzzy triggers found - need to adjust similarity thresholds")
            return False
        
    except Exception as e:
        print(f"❌ Fuzzy variations test error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 COMPREHENSIVE REAL FUZZY MATCH TEST")
    print("=" * 60)
    
    # Run tests in sequence
    results = []
    
    print("Step 1: Testing with real customer data...")
    results.append(test_real_customer_data())
    
    print("\nStep 2: Creating test customers...")
    create_success = create_test_customers()
    
    if create_success:
        print("\nStep 3: Testing fuzzy variations...")
        results.append(test_fuzzy_variations())
    
    # Summary
    print(f"\n🎯 FINAL RESULT:")
    print("=" * 60)
    
    if any(results):
        print("✅ FUZZY MATCH BACKEND IS WORKING!")
        print("🎯 NEXT STEP: Check why GUI dialog doesn't appear")
        print("\n💡 DEBUGGING TIPS:")
        print("   1. Run welcome_screen.py")
        print("   2. Try adding customer with fuzzy variation")
        print("   3. Check console output for debug messages")
        print("   4. Verify _show_duplicate_warning_dialog is called")
        
        print(f"\n🧪 TEST CASES TO TRY IN GUI:")
        print("   • Type 'Googl' (should match 'Google Inc')")
        print("   • Type 'Microsft' (should match 'Microsoft Corp')")
        print("   • Type 'tesla' (should match 'Tesla Motors')")
        
    else:
        print("❌ FUZZY MATCH NEEDS ADJUSTMENT")
        print("💡 POSSIBLE ISSUES:")
        print("   1. No customers in system to match against")
        print("   2. Similarity thresholds too high")
        print("   3. Algorithm not working correctly")
    
    print(f"\n" + "=" * 60)
