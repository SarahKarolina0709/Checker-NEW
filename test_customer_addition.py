#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Script für die Customer-Addition-Funktionalität
"""

import sys
import os
import traceback

# Stelle sicher, dass das aktuelle Verzeichnis im Python-Pfad ist
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_kunden_manager_add_customer():
    """Test der add_customer Methode im KundenManager"""
    try:
        from src.managers.kunden_manager import KundenManager
        
        # Erstelle KundenManager Instance
        manager = KundenManager(base_dir="test_projects")
        
        # Test 1: Neue Kunde hinzufügen
        print("Test 1: Neuen Kunden hinzufügen...")
        success, message, similar = manager.add_customer("Test Kunde")
        print(f"  Erfolg: {success}")
        print(f"  Nachricht: {message}")
        print(f"  Ähnliche Kunden: {similar}")
        
        # Test 2: Duplikat versuchen
        print("\nTest 2: Duplikat hinzufügen...")
        success2, message2, similar2 = manager.add_customer("Test Kunde")
        print(f"  Erfolg: {success2}")
        print(f"  Nachricht: {message2}")
        print(f"  Ähnliche Kunden: {similar2}")
        
        # Test 3: Ähnlichen Namen hinzufügen
        print("\nTest 3: Ähnlichen Namen hinzufügen...")
        success3, message3, similar3 = manager.add_customer("Test Kund")
        print(f"  Erfolg: {success3}")
        print(f"  Nachricht: {message3}")
        print(f"  Ähnliche Kunden: {similar3}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen des KundenManagers: {e}")
        traceback.print_exc()
        return False

def test_customer_manager_add_customer():
    """Test der add_customer Methode im CustomerManager"""
    try:
        from customer_manager import CustomerManager
        
        # Erstelle CustomerManager Instance
        manager = CustomerManager(customers_file="test_customers.json")
        
        # Test 1: Neue Kunde hinzufügen
        print("Test 1: Neuen Kunden hinzufügen...")
        success, message, similar = manager.add_customer("Test Customer")
        print(f"  Erfolg: {success}")
        print(f"  Nachricht: {message}")
        print(f"  Ähnliche Kunden: {similar}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen des CustomerManagers: {e}")
        traceback.print_exc()
        return False

def main():
    """Hauptfunktion für Tests"""
    print("=== Customer Addition Functionality Test ===\n")
    
    print("📋 Test 1: KundenManager (CoreKundenManager)")
    print("-" * 50)
    kunden_manager_ok = test_kunden_manager_add_customer()
    
    print("\n📋 Test 2: CustomerManager")
    print("-" * 50)
    customer_manager_ok = test_customer_manager_add_customer()
    
    print("\n=== Test-Ergebnisse ===")
    print(f"KundenManager: {'✅ OK' if kunden_manager_ok else '❌ FEHLER'}")
    print(f"CustomerManager: {'✅ OK' if customer_manager_ok else '❌ FEHLER'}")
    
    if kunden_manager_ok and customer_manager_ok:
        print("\n🎉 Alle Tests erfolgreich!")
        return 0
    else:
        print("\n⚠️ Einige Tests sind fehlgeschlagen.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
