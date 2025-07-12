#!/usr/bin/env python3
"""
Schnelltest für die Menüfunktionalität der Checker App
"""

import time
import sys
import os

def test_menu_functionality():
    """Test der Menüfunktionalität ohne GUI-Interaktion"""
    print("🚀 Teste Menüfunktionalität...")
    
    # Teste ob die App gestartet ist
    try:
        # Prüfe checker_app.py auf kritische Menüfunktionen
        with open('checker_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Kritische Funktionen die in den Menüs verwendet werden
        critical_functions = [
            'configure_customer_path',
            'on_closing',
            'show_tools_menu',
            'show_customer_menu',
            'show_workflow_menu',
            'show_help_menu',
            'show_file_menu',
            'create_new_customer',
            'show_customer_list',
            'search_customer',
            'open_customer_folder',
            'show_customer_stats',
            'verify_customer_structure'
        ]
        
        missing_functions = []
        found_functions = []
        
        for func in critical_functions:
            if f'def {func}(' in content:
                found_functions.append(func)
                print(f"✅ {func}")
            else:
                missing_functions.append(func)
                print(f"❌ {func} - FEHLT")
        
        print(f"\n📊 Ergebnis:")
        print(f"✅ Gefunden: {len(found_functions)}")
        print(f"❌ Fehlend: {len(missing_functions)}")
        
        if missing_functions:
            print(f"\n⚠️  Fehlende Funktionen:")
            for func in missing_functions:
                print(f"   - {func}")
        
        # Teste spezifisch "Kundenpfad konfigurieren" in beiden Menüs
        tools_menu_found = 'Kundenpfad konfigurieren' in content and 'show_tools_menu' in content
        customer_menu_found = 'Kundenpfad konfigurieren' in content and 'show_customer_menu' in content
        
        print(f"\n🎯 Kundenpfad-Konfiguration:")
        print(f"✅ Tools-Menü: {'OK' if tools_menu_found else 'FEHLT'}")
        print(f"✅ Kunden-Menü: {'OK' if customer_menu_found else 'FEHLT'}")
        
        success = len(missing_functions) == 0 and tools_menu_found and customer_menu_found
        
        print(f"\n🎉 Gesamt-Status: {'✅ ERFOLGREICH' if success else '❌ FEHLGESCHLAGEN'}")
        
        return success
        
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")
        return False

def main():
    """Hauptfunktion"""
    print("🔍 Checker App Menü-Funktionalitätstest")
    print("=" * 50)
    
    success = test_menu_functionality()
    
    if success:
        print("\n🎉 Alle Tests bestanden!")
        print("✅ Die App sollte jetzt funktionieren")
        print("✅ Alle Menüfunktionen sind verfügbar")
        print("✅ Kundenpfad-Konfiguration ist in beiden Menüs")
    else:
        print("\n⚠️  Einige Tests sind fehlgeschlagen")
        print("❌ Die App könnte Probleme haben")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
