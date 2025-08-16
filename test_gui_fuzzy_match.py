#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 DIRECT GUI FUZZY MATCH TEST
Testet den Fuzzy Match Dialog direkt in der GUI
"""

import customtkinter as ctk

def test_direct_fuzzy_dialog():
    """Test the fuzzy match dialog directly"""
    print("🎯 TESTING FUZZY MATCH DIALOG DIRECTLY")
    
    try:
        # Create test window
        root = ctk.CTk()
        root.title("Fuzzy Match Test")
        root.geometry("300x200")
        
        # Import WelcomeScreen
        from welcome_screen import WelcomeScreen
        
        # Create a minimal mock app
        class MockApp:
            def __init__(self):
                self.config = {}
        
        app = MockApp()
        
        # Create WelcomeScreen instance
        welcome_screen = WelcomeScreen(root, app)
        welcome_screen.pack(fill="both", expand=True)
        
        print("✅ WelcomeScreen created successfully")
        
        # Test data: similar customers that should trigger dialog
        test_customer_name = "halo"
        similar_customers = [
            {'name': 'hallo', 'score': 89},
            {'name': 'halo world', 'score': 75}
        ]
        
        print(f"🎯 Testing dialog with customer '{test_customer_name}' and {len(similar_customers)} similar")
        
        # Schedule dialog to appear after 1 second
        def show_test_dialog():
            try:
                welcome_screen._show_duplicate_warning_dialog(test_customer_name, similar_customers)
                print("🚀 Dialog called successfully!")
            except Exception as e:
                print(f"❌ Dialog error: {e}")
                import traceback
                traceback.print_exc()
        
        root.after(1000, show_test_dialog)
        
        # Create a close button for testing
        close_btn = ctk.CTkButton(
            welcome_screen,
            text="Test Fuzzy Dialog",
            command=lambda: welcome_screen._show_duplicate_warning_dialog(test_customer_name, similar_customers)
        )
        close_btn.pack(pady=20)
        
        print("🎮 GUI Test Window ready")
        print("   → Click 'Test Fuzzy Dialog' button to test manually")
        print("   → Dialog should appear automatically in 1 second")
        
        # Run the GUI
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ Direct GUI test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_add_customer_gui_flow():
    """Test the complete add customer GUI flow that should trigger fuzzy match"""
    print("🔄 TESTING COMPLETE ADD CUSTOMER GUI FLOW")
    
    try:
        # Create test window
        root = ctk.CTk()
        root.title("Add Customer Fuzzy Test")
        root.geometry("800x600")
        
        from welcome_screen import WelcomeScreen
        
        class MockApp:
            def __init__(self):
                self.config = {}
        
        app = MockApp()
        welcome_screen = WelcomeScreen(root, app)
        welcome_screen.pack(fill="both", expand=True)
        
        print("✅ WelcomeScreen created for flow test")
        
        # Pre-fill customer entry with fuzzy match candidate
        def setup_fuzzy_test():
            try:
                # Find customer entry widget
                if hasattr(welcome_screen, 'customer_entry') and welcome_screen.customer_entry:
                    welcome_screen.customer_entry.delete(0, 'end')
                    welcome_screen.customer_entry.insert(0, "halo")  # This should match "hallo"
                    print("✅ Customer entry filled with 'halo'")
                    
                    # Simulate clicking add button
                    welcome_screen._add_customer()
                    print("🚀 _add_customer() called - dialog should appear if fuzzy match works")
                else:
                    print("⚠️ customer_entry not found")
                    
            except Exception as e:
                print(f"❌ Setup fuzzy test error: {e}")
                import traceback
                traceback.print_exc()
        
        # Schedule the test
        root.after(2000, setup_fuzzy_test)
        
        # Create manual test button
        test_btn = ctk.CTkButton(
            welcome_screen,
            text="Manual Fuzzy Test (Add 'halo')",
            command=setup_fuzzy_test
        )
        test_btn.pack(pady=10)
        
        print("🎮 Complete GUI Flow Test ready")
        print("   → Automatic test will run in 2 seconds")  
        print("   → Or click 'Manual Fuzzy Test' button")
        print("   → Should trigger fuzzy match dialog for 'halo' → 'hallo'")
        
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI flow test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 DIRECT GUI FUZZY MATCH TESTING")
    print("=" * 50)
    print("Choose test:")
    print("1. Direct Dialog Test")
    print("2. Complete GUI Flow Test")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_direct_fuzzy_dialog()
    elif choice == "2":
        test_add_customer_gui_flow()
    else:
        print("Running both tests...")
        print("\n🎯 TEST 1: Direct Dialog")
        print("-" * 30)
        test_direct_fuzzy_dialog()
        
        print("\n🔄 TEST 2: Complete GUI Flow") 
        print("-" * 30)
        test_add_customer_gui_flow()
