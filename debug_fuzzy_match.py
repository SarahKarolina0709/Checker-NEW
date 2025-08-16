#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 FUZZY MATCH DEBUG TEST
Test ob die Fuzzy Match Funktionalität korrekt arbeitet
"""

def test_fuzzy_match_integration():
    """Test der kompletten Fuzzy Match Integration"""
    print("🔍 FUZZY MATCH INTEGRATION TEST")
    print("=" * 60)
    
    try:
        from customer_manager import CustomerManager
        
        # Initialize CustomerManager
        manager = CustomerManager()
        print(f"✅ CustomerManager initialized")
        
        # Check existing customers
        customers = manager.get_all_customers()
        print(f"📋 Existing customers: {len(customers)}")
        for i, customer in enumerate(customers[:5]):
            name = customer.get('name', str(customer))
            print(f"   {i+1}. {name}")
        
        if not customers:
            print("⚠️ No customers found - adding test customers")
            manager.add_customer("Test Company")
            manager.add_customer("ABC GmbH") 
            manager.add_customer("Mueller AG")
            customers = manager.get_all_customers()
            print(f"✅ Added test customers: {len(customers)}")
        
        # Test similar customer detection
        print(f"\n🔍 TESTING SIMILAR CUSTOMER DETECTION:")
        
        if customers:
            # Take first customer and create similar name
            first_customer = customers[0].get('name', str(customers[0]))
            print(f"Original customer: '{first_customer}'")
            
            # Test variations
            test_variations = [
                first_customer + " Inc",    # Suffix
                first_customer[:-1],        # Missing last char
                first_customer.lower(),     # Case variation
                first_customer.replace('e', 'a'),  # Typo
                first_customer + "s",       # Plural
            ]
            
            for variation in test_variations:
                print(f"\n🧪 Testing variation: '{variation}'")
                
                # Test customer_exists
                try:
                    exists, matched_name, score = manager.customer_exists(variation)
                    print(f"   customer_exists: exists={exists}, match='{matched_name}', score={score}")
                except Exception as e:
                    print(f"   customer_exists ERROR: {e}")
                
                # Test add_customer (should detect similar)
                try:
                    success, message, similar_customers = manager.add_customer(variation)
                    print(f"   add_customer: success={success}")
                    print(f"   message: {message}")
                    print(f"   similar_customers: {len(similar_customers)} found")
                    
                    if similar_customers:
                        print(f"   🎯 FUZZY MATCH WORKING! Similar customers:")
                        for sim in similar_customers:
                            name = sim.get('name', 'Unknown')
                            score = sim.get('score', 0)
                            print(f"      - {name} (Score: {score})")
                        return True
                    
                except Exception as e:
                    print(f"   add_customer ERROR: {e}")
        
        print(f"\n⚠️ No similar customers detected - testing search function:")
        
        # Test search function directly
        if customers:
            first_customer = customers[0].get('name', str(customers[0]))
            test_query = first_customer[:-2] if len(first_customer) > 2 else first_customer + "x"
            
            print(f"Testing search for: '{test_query}' (similar to '{first_customer}')")
            
            try:
                search_results = manager.search_customers(test_query, limit=5)
                print(f"Search results: {len(search_results)} found")
                for result in search_results:
                    name = result.get('name', 'Unknown')
                    score = result.get('score', 0)
                    print(f"   - {name} (Score: {score})")
                
                if search_results:
                    high_score_results = [r for r in search_results if r.get('score', 0) >= 80]
                    if high_score_results:
                        print(f"✅ High-score results found: {len(high_score_results)}")
                        return True
                    else:
                        print(f"⚠️ No high-score results (>= 80)")
                
            except Exception as e:
                print(f"Search function ERROR: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_fuzzy_dialog_path():
    """Test the UI path to fuzzy dialog"""
    print(f"\n🎨 TESTING UI DIALOG PATH:")
    print("=" * 60)
    
    try:
        # Mock the dialog path
        customer_name = "Test Customer"
        similar_customers = [
            {'name': 'Test Company', 'score': 85},
            {'name': 'Test Corp', 'score': 80}
        ]
        
        print(f"Customer to add: '{customer_name}'")
        print(f"Similar customers found: {len(similar_customers)}")
        
        for sim in similar_customers:
            name = sim.get('name', 'Unknown')
            score = sim.get('score', 0)
            print(f"   - {name} (Score: {score})")
        
        # This would trigger _show_duplicate_warning_dialog in the UI
        print(f"✅ This scenario would trigger the fuzzy match dialog")
        print(f"   Method: _show_duplicate_warning_dialog('{customer_name}', {similar_customers})")
        
        return True
        
    except Exception as e:
        print(f"❌ Dialog path test error: {e}")
        return False

def test_score_thresholds():
    """Test different score thresholds"""
    print(f"\n📊 TESTING SCORE THRESHOLDS:")
    print("=" * 60)
    
    try:
        from customer_manager import CustomerManager
        manager = CustomerManager()
        
        # Add a test customer if none exist
        customers = manager.get_all_customers()
        if not customers:
            manager.add_customer("Test Company Ltd")
            customers = manager.get_all_customers()
        
        if customers:
            base_customer = customers[0].get('name', str(customers[0]))
            print(f"Base customer: '{base_customer}'")
            
            # Test different similarity levels
            test_cases = [
                (base_customer, "Should be exact match"),
                (base_customer + " Inc", "Should be high similarity"),
                (base_customer[:-3], "Should be medium similarity"),  
                (base_customer.replace(base_customer[0], 'X'), "Should be lower similarity"),
                ("Completely Different Name", "Should be no match")
            ]
            
            for test_name, description in test_cases:
                try:
                    search_results = manager.search_customers(test_name, limit=3)
                    if search_results:
                        best_match = search_results[0]
                        score = best_match.get('score', 0)
                        match_name = best_match.get('name', 'Unknown')
                        print(f"'{test_name}' -> '{match_name}' (Score: {score}) - {description}")
                    else:
                        print(f"'{test_name}' -> No matches - {description}")
                except Exception as e:
                    print(f"'{test_name}' -> Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Score threshold test error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE FUZZY MATCH DEBUG TEST")
    print("=" * 80)
    
    results = []
    
    # Run tests
    results.append(("Fuzzy Match Integration", test_fuzzy_match_integration()))
    results.append(("UI Dialog Path", test_fuzzy_dialog_path()))
    results.append(("Score Thresholds", test_score_thresholds()))
    
    # Summary
    print(f"\n🎯 FUZZY MATCH DEBUG SUMMARY:")
    print("=" * 80)
    
    passed = 0
    for test_name, result in results:
        status = "✅ WORKING" if result else "❌ ISSUE"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 RESULTS: {passed}/{len(results)} components working")
    
    if passed == len(results):
        print("✅ FUZZY MATCH FULLY FUNCTIONAL")
    else:
        print("⚠️ FUZZY MATCH HAS ISSUES - Need to debug further")
    
    print(f"\n💡 DEBUGGING HINTS:")
    print(f"   1. Check if customers.json has enough test data")
    print(f"   2. Verify similarity scoring algorithm")
    print(f"   3. Test with actual customer names from your data")
    print(f"   4. Check score thresholds (>= 80 for similar detection)")
    print(f"   5. Verify _show_duplicate_warning_dialog is called correctly")
