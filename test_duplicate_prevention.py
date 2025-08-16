#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 TEST DUPLICATE PREVENTION IN MAIN APP
========================================

Testet die korrigierte Duplikat-Erkennung in der Haupt-Anwendung.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import json
import tkinter as tk
import customtkinter as ctk

# Light Mode erzwingen
ctk.set_appearance_mode("light")

def test_duplicate_prevention():
    """Teste die Duplikat-Prävention in einer minimalen GUI"""
    print("🧪 TESTING DUPLICATE PREVENTION IN MAIN APP")
    print("=" * 50)
    
    # Erstelle eine minimale App
    root = ctk.CTk()
    root.title("Duplicate Test")
    root.geometry("600x400")
    
    # Simuliere die Welcome Screen Klasse
    try:
        from welcome_screen import WelcomeScreen
        
        # Erstelle Welcome Screen
        app = WelcomeScreen(root)
        
        print("✅ Welcome Screen created successfully")
        
        # Teste Duplikat-Verhalten programmatisch
        test_customer_name = "TestDuplicate"
        
        print(f"\n1️⃣ Adding customer '{test_customer_name}' first time...")
        
        # Simuliere Eingabe
        if hasattr(app, 'customer_entry') and app.customer_entry:
            app.customer_entry.delete(0, 'end')
            app.customer_entry.insert(0, test_customer_name)
            
            # Füge Kunden hinzu
            app._add_customer()
            
            print(f"   Current customer: {getattr(app, 'current_customer', 'None')}")
            
            # Warte kurz
            root.update()
            time.sleep(0.5)
            
            print(f"\n2️⃣ Trying to add '{test_customer_name}' again (should show warning)...")
            
            # Versuche denselben Kunden nochmal hinzuzufügen
            app.customer_entry.delete(0, 'end')
            app.customer_entry.insert(0, test_customer_name)
            
            # Füge Kunden hinzu (sollte Warnung zeigen)
            app._add_customer()
            
            print(f"   Current customer after duplicate: {getattr(app, 'current_customer', 'None')}")
            
            # Teste Case-insensitive
            print(f"\n3️⃣ Trying to add '{test_customer_name.lower()}' (lowercase, should warn)...")
            
            app.customer_entry.delete(0, 'end')
            app.customer_entry.insert(0, test_customer_name.lower())
            
            app._add_customer()
            
            print(f"   Current customer after case test: {getattr(app, 'current_customer', 'None')}")
            
            root.update()
            
        else:
            print("❌ Customer entry not found")
            
        # Zeige GUI kurz (für visuellen Test)
        print(f"\n📱 Showing GUI for 3 seconds...")
        root.after(3000, root.quit)
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    test_duplicate_prevention()
    
    print("\n" + "=" * 50)
    print("🎯 EXPECTED BEHAVIOR:")
    print("✅ First add → Success")
    print("⚠️  Second add → Warning + auto-select") 
    print("⚠️  Case test → Warning + auto-select")
    print("📊 Customer should remain selected throughout")
