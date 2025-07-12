#!/usr/bin/env python3
"""
Einfacher Test für die Menüfunktionalität - prüft ob "Kundenpfad konfigurieren" in beiden Menüs verfügbar ist
"""

import os
import sys

# Füge den aktuellen Pfad zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_menu_items():
    """Test der Menüeinträge ohne GUI-Erstellung"""
    print("🔍 Prüfe Menüeinträge für 'Kundenpfad konfigurieren'...")
    
    try:
        # Lese die checker_app.py Datei und prüfe die Menüs
        with open('checker_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Prüfe Tools-Menü
        tools_menu_found = False
        customer_menu_found = False
        
        lines = content.split('\n')
        in_tools_menu = False
        in_customer_menu = False
        
        for i, line in enumerate(lines):
            # Tools-Menü Detection
            if 'def show_tools_menu(self):' in line:
                in_tools_menu = True
                print(f"✅ Tools-Menü gefunden in Zeile {i+1}")
                continue
            
            # Customer-Menü Detection
            if 'def show_customer_menu(self):' in line:
                in_customer_menu = True
                print(f"✅ Kunden-Menü gefunden in Zeile {i+1}")
                continue
            
            # Ende der Menüs Detection
            if in_tools_menu and ('def ' in line and 'show_tools_menu' not in line):
                in_tools_menu = False
            
            if in_customer_menu and ('def ' in line and 'show_customer_menu' not in line):
                in_customer_menu = False
            
            # Suche nach "Kundenpfad konfigurieren"
            if in_tools_menu and 'Kundenpfad konfigurieren' in line:
                tools_menu_found = True
                print(f"✅ 'Kundenpfad konfigurieren' im Tools-Menü gefunden (Zeile {i+1})")
            
            if in_customer_menu and 'Kundenpfad konfigurieren' in line:
                customer_menu_found = True
                print(f"✅ 'Kundenpfad konfigurieren' im Kunden-Menü gefunden (Zeile {i+1})")
        
        # Prüfe configure_customer_path Funktion
        if 'def configure_customer_path(self):' in content:
            print("✅ configure_customer_path Funktion gefunden")
            function_found = True
        else:
            print("❌ configure_customer_path Funktion nicht gefunden")
            function_found = False
        
        # Zusammenfassung
        print("\n📋 Test-Ergebnis:")
        print(f"- Tools-Menü: {'✅ OK' if tools_menu_found else '❌ FEHLT'}")
        print(f"- Kunden-Menü: {'✅ OK' if customer_menu_found else '❌ FEHLT'}")
        print(f"- Funktion: {'✅ OK' if function_found else '❌ FEHLT'}")
        
        if tools_menu_found and customer_menu_found and function_found:
            print("\n🎉 Alle Tests erfolgreich! 'Kundenpfad konfigurieren' ist in beiden Menüs verfügbar.")
            return True
        else:
            print("\n⚠️  Einige Tests sind fehlgeschlagen.")
            return False
            
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")
        return False

def check_menu_structure():
    """Prüft die komplette Menüstruktur"""
    print("\n🔍 Prüfe vollständige Menüstruktur...")
    
    try:
        with open('checker_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        expected_functions = [
            'show_tools_menu',
            'show_customer_menu', 
            'show_workflow_menu',
            'show_help_menu',
            'configure_customer_path'
        ]
        
        found_functions = []
        for func in expected_functions:
            if f'def {func}(self):' in content:
                found_functions.append(func)
                print(f"✅ {func} gefunden")
            else:
                print(f"❌ {func} fehlt")
        
        print(f"\n📊 Gefundene Funktionen: {len(found_functions)}/{len(expected_functions)}")
        
        return len(found_functions) == len(expected_functions)
        
    except Exception as e:
        print(f"❌ Fehler bei Strukturprüfung: {e}")
        return False

def main():
    """Hauptfunktion"""
    print("🚀 Starte Menüstruktur-Test")
    print("=" * 50)
    
    # Test 1: Menüeinträge
    success1 = test_menu_items()
    
    # Test 2: Menüstruktur 
    success2 = check_menu_structure()
    
    print("\n" + "=" * 50)
    print("📊 Gesamt-Ergebnis:")
    
    if success1 and success2:
        print("🎉 Alle Tests erfolgreich!")
        print("✅ Die Menüs sind korrekt implementiert.")
        print("✅ 'Kundenpfad konfigurieren' ist in beiden Menüs verfügbar.")
        return True
    else:
        print("⚠️  Einige Tests sind fehlgeschlagen.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
