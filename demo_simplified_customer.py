#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Vereinfachtes Kunden-Hinzufügen System

Zeigt wie das neue, vereinfachte System funktioniert:
- Nur Pflichtfelder (Name, Code, optional Company)
- Automatische Code-Generierung
- Ordner-Erstellung mit Firmennamen
- Optionale Felder können später hinzugefügt werden
"""

import customtkinter as ctk
import sys
import os
import json

# Pfad konfigurieren
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from customer_management_utils import CustomerManager

def demo_simplified_customer_system():
    """Demo des vereinfachten Kundensystems."""
    
    print("=== DEMO: Vereinfachtes Kunden-Hinzufügen System ===\n")
    
    # Customer Manager laden
    cm = CustomerManager()
    
    print("1. AKTUELLER STAND:")
    print(f"   📊 Anzahl Kunden: {len(cm.customers_data)}")
    print()
    
    print("2. NEUEN KUNDEN HINZUFÜGEN (Vereinfacht):")
    print("   Nur noch diese Felder nötig:")
    print("   ✅ Firmenname (Pflicht)")
    print("   ✅ Kürzel (automatisch generiert, optional anpassbar)")
    print("   ⚪ Vollständiger Firmenname (optional)")
    print()
    print("   Nicht mehr nötig beim Erstellen:")
    print("   ❌ Ansprechpartner")
    print("   ❌ E-Mail")
    print("   ❌ Telefon")
    print("   ❌ Adresse")
    print("   ❌ Notizen")
    print()
    
    # Beispiel-Kunde erstellen
    print("3. BEISPIEL - Neuer Kunde:")
    print("   Eingabe: 'Demo Software GmbH'")
    
    # Simuliere Kunde hinzufügen
    test_customer_id = cm.add_new_customer(
        name="Demo Software GmbH",
        code="DEM",
        company="Demo Software GmbH & Co. KG"
    )
    
    if test_customer_id:
        print(f"   ✅ Kunde erstellt mit ID: {test_customer_id}")
        
        # Ordnername anzeigen
        folder_name = cm.get_customer_folder_name(test_customer_id)
        print(f"   📁 Ordnername: {folder_name}")
        
        # Upload-Ordner erstellen
        upload_folder = cm.create_upload_folder(test_customer_id)
        print(f"   📤 Upload-Ordner: {upload_folder}")
        
        # Kundendaten anzeigen
        customer_data = cm.customers_data[test_customer_id]
        print("\n   📋 Gespeicherte Daten:")
        for key, value in customer_data.items():
            if key in ['name', 'code', 'company', 'contact', 'email']:
                status = "✅" if value else "⚪"
                print(f"      {status} {key}: '{value}'")
    
    print("\n4. VORTEILE DES VEREINFACHTEN SYSTEMS:")
    print("   🚀 Schnellere Kundenerstellung")
    print("   🎯 Fokus auf wesentliche Daten")
    print("   📝 Optionale Felder später ergänzbar")
    print("   🏢 Ordner nach Firmennamen statt Kürzel")
    print("   ✨ Bessere Benutzerfreundlichkeit")
    
    print("\n5. AKTUELLER STAND NACH DEMO:")
    print(f"   📊 Anzahl Kunden: {len(cm.customers_data)}")
    
    # Aufräumen - Test-Kunde wieder entfernen
    if test_customer_id and test_customer_id in cm.customers_data:
        del cm.customers_data[test_customer_id]
        cm.save_customers_data()
        print("   🧹 Demo-Kunde wurde wieder entfernt")

if __name__ == "__main__":
    demo_simplified_customer_system()
