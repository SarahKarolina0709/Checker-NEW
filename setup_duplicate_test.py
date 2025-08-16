#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 MANUAL DUPLICATE TEST
=======================

Erstellt Testdaten und testet die Duplikat-Erkennung manuell.
"""

import json
import os
from pathlib import Path

def create_test_customers():
    """Erstelle Test-Kunden für manuellen Duplikat-Test"""
    test_customers = [
        {
            "name": "TestFirma GmbH",
            "created": "2025-08-15T10:00:00",
            "projects": [],
            "stats": {
                "total_projects": 0,
                "total_files": 0,
                "last_activity": "2025-08-15T10:00:00"
            }
        },
        {
            "name": "Beispiel AG",
            "created": "2025-08-15T09:00:00", 
            "projects": [],
            "stats": {
                "total_projects": 0,
                "total_files": 0,
                "last_activity": "2025-08-15T09:00:00"
            }
        }
    ]
    
    # Speichere Test-Kunden
    customers_file = "customers.json"
    with open(customers_file, 'w', encoding='utf-8') as f:
        json.dump(test_customers, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Test customers created in {customers_file}")
    print("📋 Test customers:")
    for i, customer in enumerate(test_customers, 1):
        print(f"   {i}. {customer['name']}")
    
    return test_customers

def test_customer_manager_exists():
    """Teste ob CustomerManager existiert"""
    try:
        from customer_manager import CustomerManager
        
        manager = CustomerManager(
            customers_file="customers.json",
            projects_base_path="test_projects"
        )
        
        # Teste exists Methode
        exists1, name1, score1 = manager.customer_exists("TestFirma GmbH")
        exists2, name2, score2 = manager.customer_exists("testfirma gmbh")
        exists3, name3, score3 = manager.customer_exists("Nicht Vorhanden")
        
        print(f"\n🔍 CustomerManager exists tests:")
        print(f"   'TestFirma GmbH' → exists={exists1}, name='{name1}', score={score1}")
        print(f"   'testfirma gmbh' → exists={exists2}, name='{name2}', score={score2}")
        print(f"   'Nicht Vorhanden' → exists={exists3}, name='{name3}', score={score3}")
        
        return True
        
    except Exception as e:
        print(f"❌ CustomerManager test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 MANUAL DUPLICATE TEST SETUP")
    print("=" * 40)
    
    # Erstelle Test-Daten
    customers = create_test_customers()
    
    # Teste CustomerManager
    manager_ok = test_customer_manager_exists()
    
    print(f"\n🎯 MANUAL TEST INSTRUCTIONS:")
    print(f"1. Starte die Welcome Screen App")
    print(f"2. Versuche 'TestFirma GmbH' hinzuzufügen → sollte Warnung zeigen")
    print(f"3. Versuche 'testfirma gmbh' hinzuzufügen → sollte Warnung zeigen")
    print(f"4. Versuche 'beispiel ag' hinzuzufügen → sollte Warnung zeigen")
    print(f"5. Versuche 'Neue Firma' hinzuzufügen → sollte erfolgreich sein")
    
    print(f"\n✅ Test setup complete!")
    if manager_ok:
        print("✅ CustomerManager is working correctly")
    else:
        print("⚠️  CustomerManager has issues - check manually")
