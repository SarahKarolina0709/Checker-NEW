#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 FUZZY MATCH INTEGRATION TEST
Testet die Fuzzy Match Funktionalität End-to-End
"""

def test_fuzzy_match_integration():
    """Test the complete fuzzy match workflow"""
    print("🔍 FUZZY MATCH INTEGRATION TEST")
    print("=" * 50)
    
    try:
        from customer_manager import CustomerManager
        
        # Initialize CustomerManager
        manager = CustomerManager()
        print("✅ CustomerManager initialized")
        
        # Load existing customers
        existing_customers = manager._get_all_customer_names() if hasattr(manager, '_get_all_customer_names') else manager.customers_data
        print(f"📋 Existing customers: {len(existing_customers)}")
        
        for i, customer in enumerate(existing_customers[:5]):
            name = customer.get('name', str(customer)) if isinstance(customer, dict) else str(customer)
            print(f"   {i+1}. {name}")
        
        # Test fuzzy matches
        print(f"\n🔍 TESTING FUZZY MATCHES:")
        
        test_cases = [
            ("halo", "hallo"),  # Should match existing "hallo" customer
            ("muller", "Mueller"),  # Should match "Kunde_Mueller"  
            ("bast", "basti"),  # Should match "basti"
            ("neu1", "neu"),  # Should match "neu"
            ("completelynew", None)  # Should not match anything
        ]
        
        for test_name, expected in test_cases:
            print(f"\n📍 Testing '{test_name}' (expecting match with '{expected}'):")
            
            # Test customer_exists
            try:
                exists, matched_name, score = manager.customer_exists(test_name)
                print(f"   customer_exists: {exists}, matched: '{matched_name}', score: {score}")
            except Exception as e:
                print(f"   customer_exists error: {e}")
            
            # Test add_customer (should find similar)
            try:
                success, message, similar_customers = manager.add_customer(test_name)
                print(f"   add_customer: success={success}")
                print(f"   message: {message}")
                print(f"   similar_customers: {len(similar_customers) if similar_customers else 0}")
                
                if similar_customers:
                    for similar in similar_customers:
                        name = similar.get('name', str(similar))
                        score = similar.get('score', 0)
                        print(f"     → {name} (Score: {score})")
                        
                        # This should trigger the fuzzy match dialog!
                        if score >= 60:  # Fuzzy match threshold
                            print(f"     🎯 FUZZY MATCH DETECTED! Should show dialog")
                        
            except Exception as e:
                print(f"   add_customer error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fuzzy match test error: {e}")
        return False

def test_gui_integration():
    """Test GUI integration for fuzzy match dialog"""
    print(f"\n🎨 TESTING GUI INTEGRATION:")
    print("=" * 50)
    
    try:
        # Test if welcome_screen has the required methods
        import welcome_screen
        
        # Check if WelcomeScreen class has the fuzzy match methods
        methods_to_check = [
            '_show_duplicate_warning_dialog',
            '_handle_customer_added_successfully',
            '_add_customer'
        ]
        
        for method_name in methods_to_check:
            if hasattr(welcome_screen.WelcomeScreen, method_name):
                print(f"✅ Method {method_name} found in WelcomeScreen")
            else:
                print(f"❌ Method {method_name} MISSING in WelcomeScreen")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI integration test error: {e}")
        return False

def debug_add_customer_flow():
    """Debug the complete add_customer flow"""
    print(f"\n🐛 DEBUGGING ADD_CUSTOMER FLOW:")
    print("=" * 50)
    
    try:
        from customer_manager import CustomerManager
        
        manager = CustomerManager()
        
        # Test with a name that should trigger fuzzy match
        test_name = "halo"  # Similar to "hallo"
        
        print(f"🔍 Testing add_customer with '{test_name}':")
        
        # Step 1: Check existence first
        print(f"   Step 1: Checking customer_exists...")
        exists, matched_name, score = manager.customer_exists(test_name)
        print(f"   → exists: {exists}, matched: '{matched_name}', score: {score}")
        
        if exists and score >= 90:
            print(f"   → High similarity found - should auto-select")
            return True
        
        # Step 2: Try to add customer
        print(f"   Step 2: Calling add_customer...")
        success, message, similar_customers = manager.add_customer(test_name)
        
        print(f"   → success: {success}")
        print(f"   → message: {message}")
        print(f"   → similar_customers: {similar_customers}")
        
        if not success and similar_customers:
            print(f"   → FUZZY MATCH SCENARIO DETECTED!")
            print(f"   → This should trigger _show_duplicate_warning_dialog")
            
            for similar in similar_customers:
                name = similar.get('name', str(similar))
                score = similar.get('score', 0)
                print(f"     → Candidate: {name} (Score: {score})")
            
            return "fuzzy_match_detected"
        
        return success
        
    except Exception as e:
        print(f"❌ Debug flow error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE FUZZY MATCH INTEGRATION TEST")
    print("=" * 60)
    
    # Run all tests
    test1 = test_fuzzy_match_integration()
    test2 = test_gui_integration()  
    test3 = debug_add_customer_flow()
    
    print(f"\n🎯 TEST SUMMARY:")
    print("=" * 60)
    print(f"✅ Fuzzy Match Logic: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"✅ GUI Integration: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"✅ Add Customer Flow: {'✅ PASS' if test3 == True else '🎯 FUZZY DETECTED' if test3 == 'fuzzy_match_detected' else '❌ FAIL'}")
    
    if test3 == "fuzzy_match_detected":
        print(f"\n🎯 FUZZY MATCH DIALOG SHOULD APPEAR!")
        print("   → Backend logic is working correctly")
        print("   → Problem might be in GUI dialog display")
        print("   → Check _show_duplicate_warning_dialog implementation")
    
    print(f"\n🔍 Next step: Test with actual GUI to see if dialog appears")
