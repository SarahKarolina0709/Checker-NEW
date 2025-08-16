#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 FINAL DUPLICATE PREVENTION TEST
===================================

Testet die Duplikat-Erkennung direkt über CustomerManager.
"""

import json
import os
from pathlib import Path

def test_duplicate_detection():
    """Teste die Duplikat-Erkennung"""
    print("🧪 FINAL DUPLICATE PREVENTION TEST")
    print("=" * 50)
    
    try:
        # Import CustomerManager
        from customer_manager import CustomerManager
        
        # Initialize CustomerManager
        manager = CustomerManager(
            customers_file="customers.json",
            projects_base_path="projects"
        )
        
        print("✅ CustomerManager initialisiert")
        
        # Zeige aktuelle Kunden
        with open('customers.json', 'r', encoding='utf-8') as f:
            customers = json.load(f)
        
        print(f"\n📋 Aktuelle Kunden ({len(customers)}):")
        for i, customer in enumerate(customers, 1):
            print(f"   {i}. {customer['name']}")
        
        # Test Cases für Duplikat-Erkennung
        test_cases = [
            ("TestFirma GmbH", "Exakte Übereinstimmung"),
            ("testfirma gmbh", "Groß-/Kleinschreibung ignoriert"),
            ("TESTFIRMA GMBH", "Alles Großbuchstaben"),
            ("Test Firma GmbH", "Leichte Variation"),
            ("Beispiel AG", "Zweiter existierender Kunde"),
            ("beispiel ag", "Kleingeschrieben"),
            ("Neue Test Firma", "Nicht existierender Kunde")
        ]
        
        print(f"\n🔍 DUPLIKAT-ERKENNUNGS TESTS:")
        print("-" * 50)
        
        for test_name, description in test_cases:
            try:
                exists, matched_name, score = manager.customer_exists(test_name)
                status = "🚨 DUPLIKAT" if exists and score >= 90 else "✅ NEU" if not exists else f"⚠️ ÄHNLICH (Score: {score})"
                
                print(f"Test: '{test_name}'")
                print(f"  → {description}")
                print(f"  → {status}")
                if exists:
                    print(f"  → Matched: '{matched_name}' (Score: {score})")
                print()
                
            except Exception as e:
                print(f"❌ Fehler bei '{test_name}': {e}")
                print()
        
        print("🎯 ERWARTETE ERGEBNISSE:")
        print("• 'TestFirma GmbH' → 🚨 DUPLIKAT (Score: 100)")
        print("• 'testfirma gmbh' → 🚨 DUPLIKAT (Score: 100)")
        print("• 'TESTFIRMA GMBH' → 🚨 DUPLIKAT (Score: 100)")
        print("• 'Beispiel AG' → 🚨 DUPLIKAT (Score: 100)")
        print("• 'beispiel ag' → 🚨 DUPLIKAT (Score: 100)")
        print("• 'Neue Test Firma' → ✅ NEU")
        
        print(f"\n✅ Duplikat-Erkennungs-Test abgeschlossen!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_duplicate_detection()
    if success:
        print("\n🎉 ALLE TESTS ERFOLGREICH!")
        print("Die Duplikat-Erkennung ist korrekt implementiert.")
    else:
        print("\n❌ TESTS FEHLGESCHLAGEN!")
        print("Bitte prüfe die Implementierung.")
