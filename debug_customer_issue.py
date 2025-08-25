#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug-Script für Customer-Addition Problem
"""

import sys
import os

# Stelle sicher, dass das aktuelle Verzeichnis im Python-Pfad ist
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_customer_managers():
    """Debug die Customer Manager"""
    try:
        print("=== DEBUG: Customer Manager Verfügbarkeit ===")
        
        # Test 1: KundenManager
        try:
            from src.managers.kunden_manager import KundenManager
            km = KundenManager(base_dir="projects")
            print(f"✅ KundenManager importiert: {type(km)}")
            
            # Test add_customer Methode
            if hasattr(km, 'add_customer'):
                print("✅ add_customer Methode gefunden im KundenManager")
                # Test die Methode
                success, msg, similar = km.add_customer("Debug Test")
                print(f"   Test-Ergebnis: success={success}, msg='{msg}'")
            else:
                print("❌ add_customer Methode NICHT gefunden im KundenManager")
        except Exception as e:
            print(f"❌ KundenManager Import-Fehler: {e}")
        
        # Test 2: CustomerManager
        try:
            from customer_manager import CustomerManager
            cm = CustomerManager()
            print(f"✅ CustomerManager importiert: {type(cm)}")
            
            # Test add_customer Methode
            if hasattr(cm, 'add_customer'):
                print("✅ add_customer Methode gefunden im CustomerManager")
                # Test die Methode
                success, msg, similar = cm.add_customer("Debug Test 2")
                print(f"   Test-Ergebnis: success={success}, msg='{msg}'")
            else:
                print("❌ add_customer Methode NICHT gefunden im CustomerManager")
        except Exception as e:
            print(f"❌ CustomerManager Import-Fehler: {e}")
        
        print("\n=== DEBUG: Welcome Screen Initialisierung ===")
        
        # Test 3: Welcome Screen Manager-Initialisierung
        try:
            import welcome_screen
            print("✅ Welcome Screen Modul importiert")
            
            # Simuliere Manager-Initialisierung
            try:
                projects_base_path = "projects"
                
                # CustomerManager
                from customer_manager import CustomerManager
                customer_manager = CustomerManager(
                    customers_file="customers.json",
                    projects_base_path=projects_base_path
                )
                print(f"✅ CustomerManager initialisiert: {customer_manager}")
                
                # KundenManager  
                from src.managers.kunden_manager import KundenManager as CoreKundenManager
                kunden_manager = CoreKundenManager(base_dir=projects_base_path)
                print(f"✅ KundenManager initialisiert: {kunden_manager}")
                
                # Test beide add_customer Methoden
                print("\n--- Test add_customer Methoden ---")
                if hasattr(customer_manager, 'add_customer'):
                    try:
                        result1 = customer_manager.add_customer("Test Customer A")
                        print(f"CustomerManager.add_customer: {result1}")
                    except Exception as e:
                        print(f"CustomerManager.add_customer Fehler: {e}")
                
                if hasattr(kunden_manager, 'add_customer'):
                    try:
                        result2 = kunden_manager.add_customer("Test Customer B")
                        print(f"KundenManager.add_customer: {result2}")
                    except Exception as e:
                        print(f"KundenManager.add_customer Fehler: {e}")
                else:
                    print("❌ KundenManager hat KEINE add_customer Methode!")
                    
            except Exception as e:
                print(f"❌ Manager-Initialisierung Fehler: {e}")
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            print(f"❌ Welcome Screen Import-Fehler: {e}")
            
    except Exception as e:
        print(f"❌ Allgemeiner Debug-Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_customer_managers()
