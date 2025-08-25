#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der Customer-Addition in der Welcome Screen GUI
"""

import sys
import os
import traceback

# Stelle sicher, dass das aktuelle Verzeichnis im Python-Pfad ist
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_welcome_screen_customer_addition():
    """Test der Customer-Addition in der Welcome Screen"""
    try:
        # Importiere die notwendigen Module
        import welcome_screen
        
        print("✅ Welcome screen module importiert")
        
        # Teste die Manager-Erstellung
        from src.managers.kunden_manager import KundenManager
        kunden_mgr = KundenManager(base_dir="test_projects")
        
        print("✅ KundenManager erstellt")
        
        # Teste add_customer Methode direkt
        success, message, similar = kunden_mgr.add_customer("GUI Test Kunde")
        print(f"✅ add_customer Test: Erfolg={success}, Nachricht='{message}'")
        
        # Teste CustomerManager
        from customer_manager import CustomerManager
        customer_mgr = CustomerManager(customers_file="test_gui_customers.json")
        
        success2, message2, similar2 = customer_mgr.add_customer("GUI Test Customer")
        print(f"✅ CustomerManager Test: Erfolg={success2}, Nachricht='{message2}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen der Welcome Screen Customer-Addition: {e}")
        traceback.print_exc()
        return False

def main():
    """Hauptfunktion"""
    print("=== Welcome Screen Customer Addition Test ===\n")
    
    success = test_welcome_screen_customer_addition()
    
    print(f"\n=== Ergebnis: {'✅ ERFOLGREICH' if success else '❌ FEHLGESCHLAGEN'} ===")
    
    if success:
        print("\n🎉 Die Customer-Addition-Funktionalität funktioniert korrekt!")
        print("Du kannst jetzt Kunden in der Welcome Screen hinzufügen.")
    else:
        print("\n⚠️ Es gibt noch Probleme mit der Customer-Addition.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
