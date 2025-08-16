#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 LIVE FUZZY MATCH UI TEST
Test der Fuzzy Match Funktionalität direkt in der GUI
"""

import tkinter as tk
import customtkinter as ctk
import time

def test_gui_fuzzy_match():
    """Test Fuzzy Match direkt in der GUI"""
    print("🔍 LIVE GUI FUZZY MATCH TEST")
    print("=" * 60)
    
    try:
        # Import der Hauptklasse
        import sys
        import os
        sys.path.append(os.getcwd())
        
        from welcome_screen import WelcomeScreen
        
        # Mock App
        class MockApp:
            def __init__(self):
                pass
        
        # GUI erstellen
        root = ctk.CTk()
        root.title("Fuzzy Match Test")
        root.geometry("800x600")
        
        app = MockApp()
        welcome_screen = WelcomeScreen(root, app)
        welcome_screen.pack(fill="both", expand=True)
        
        # Test-Szenario vorbereiten
        def run_fuzzy_test():
            print("🧪 Running automated fuzzy match test...")
            
            # Sicherstellen, dass wir Testkunden haben
            try:
                from customer_manager import CustomerManager
                manager = CustomerManager()
                
                # Füge einen Testkunden hinzu falls nötig
                customers = manager.get_all_customers()
                if not customers or len(customers) < 2:
                    manager.add_customer("Test Company GmbH")
                    manager.add_customer("Example Corp")
                    print("✅ Added test customers")
                
                customers = manager.get_all_customers()
                if customers:
                    first_customer = customers[0].get('name', str(customers[0]))
                    print(f"🎯 Will test similarity for: {first_customer}")
                    
                    # Ähnlichen Namen erstellen
                    similar_name = first_customer + " AG"  # Suffix hinzufügen
                    
                    # In Customer Entry eingeben
                    if hasattr(welcome_screen, 'customer_entry'):
                        welcome_screen.customer_entry.delete(0, 'end')
                        welcome_screen.customer_entry.insert(0, similar_name)
                        print(f"✅ Entered similar name: {similar_name}")
                        
                        # Add Customer Button simulieren
                        root.after(1000, simulate_add_click)
                    else:
                        print("❌ Customer entry field not found")
                
            except Exception as e:
                print(f"❌ Test setup error: {e}")
        
        def simulate_add_click():
            """Simuliere Add Customer Click"""
            try:
                print("🖱️ Simulating Add Customer click...")
                
                # _add_customer direkt aufrufen
                if hasattr(welcome_screen, '_add_customer'):
                    welcome_screen._add_customer()
                    print("✅ _add_customer called")
                else:
                    print("❌ _add_customer method not found")
                
                # Dialog should appear now - close GUI after 5 seconds
                root.after(5000, root.destroy)
                
            except Exception as e:
                print(f"❌ Simulate click error: {e}")
                root.after(2000, root.destroy)
        
        def check_dialog():
            """Prüfe ob Dialog angezeigt wird"""
            try:
                # Check for top-level windows (dialog)
                dialogs = [w for w in root.winfo_children() if isinstance(w, ctk.CTkToplevel)]
                if dialogs:
                    print(f"✅ FUZZY MATCH DIALOG FOUND: {len(dialogs)} dialog(s)")
                    for dialog in dialogs:
                        print(f"   Dialog title: {dialog.title()}")
                else:
                    print("⚠️ No dialog windows found")
                
                # Check again in 1 second
                root.after(1000, check_dialog)
                
            except Exception as e:
                print(f"Dialog check error: {e}")
        
        # Starte Tests
        root.after(500, run_fuzzy_test)  # Nach GUI-Initialisierung
        root.after(2000, check_dialog)   # Dialog-Prüfung starten
        
        print("🚀 Starting GUI - Fuzzy match test will run automatically...")
        print("   Watch for dialog popup when similar customer is detected!")
        
        # GUI starten
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI test error: {e}")
        return False

def manual_test_instructions():
    """Manuelle Test-Anweisungen"""
    print(f"\n📋 MANUAL FUZZY MATCH TEST INSTRUCTIONS:")
    print("=" * 60)
    
    instructions = [
        "1. Start welcome_screen.py",
        "2. Check existing customers in customers.json",
        "3. Enter similar customer name (e.g. if 'Test' exists, enter 'Test GmbH')",
        "4. Click 'Kunde hinzufügen' button",
        "5. Check if fuzzy match dialog appears",
        "6. If no dialog: Check console for error messages"
    ]
    
    for instruction in instructions:
        print(f"   {instruction}")
    
    print(f"\n🔍 DEBUGGING CHECKLIST:")
    debug_items = [
        "✅ CustomerManager.add_customer() returns similar_customers",
        "✅ _add_customer() calls _show_duplicate_warning_dialog()",
        "✅ Dialog window is created with CTkToplevel",
        "⚠️ Check if dialog.grab_set() works correctly",
        "⚠️ Check if dialog is behind main window"
    ]
    
    for item in debug_items:
        print(f"   {item}")

if __name__ == "__main__":
    print("🔍 FUZZY MATCH UI INTEGRATION TEST")
    print("=" * 80)
    
    # Ask user which test to run
    print("\nSelect test mode:")
    print("1. Automated GUI test (recommended)")
    print("2. Show manual test instructions")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            success = test_gui_fuzzy_match()
            if success:
                print("\n✅ GUI test completed - check console output above")
            else:
                print("\n❌ GUI test failed")
        elif choice == "2":
            manual_test_instructions()
        else:
            print("Invalid choice - showing manual instructions")
            manual_test_instructions()
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        manual_test_instructions()
    
    print(f"\n" + "=" * 80)
    print("Fuzzy Match UI Test Complete!")
