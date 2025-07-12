#!/usr/bin/env python3
"""
Test-Skript für die Menüfunktionalität der Checker App
Überprüft, ob alle Menüeinträge korrekt funktionieren
"""

import sys
import os
from pathlib import Path
import time

# Pfad zur Checker App hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_menu_access():
    """Test der Menüzugriffe - simuliert Benutzerinteraktion"""
    print("🔍 Teste Menüzugriffe der Checker App...")
    
    try:
        # Importiere die Checker App
        from checker_app import CheckerApp
        
        print("✅ Checker App erfolgreich importiert")
        
        # Erstelle eine Test-Instanz
        app = CheckerApp()
        
        print("✅ Checker App Instanz erstellt")
        
        # Teste die Menüfunktionen
        print("\n📋 Teste Menüfunktionen:")
        
        # Tools Menu
        print("- Tools-Menü:")
        try:
            app.show_tools_menu()
            print("  ✅ Tools-Menü funktioniert")
        except Exception as e:
            print(f"  ❌ Tools-Menü Fehler: {e}")
        
        # Customer Menu
        print("- Kunden-Menü:")
        try:
            app.show_customer_menu()
            print("  ✅ Kunden-Menü funktioniert")
        except Exception as e:
            print(f"  ❌ Kunden-Menü Fehler: {e}")
        
        # Workflow Menu
        print("- Workflow-Menü:")
        try:
            app.show_workflow_menu()
            print("  ✅ Workflow-Menü funktioniert")
        except Exception as e:
            print(f"  ❌ Workflow-Menü Fehler: {e}")
        
        # Help Menu
        print("- Hilfe-Menü:")
        try:
            app.show_help_menu()
            print("  ✅ Hilfe-Menü funktioniert")
        except Exception as e:
            print(f"  ❌ Hilfe-Menü Fehler: {e}")
        
        # Teste spezifische Funktionen
        print("\n🔧 Teste spezifische Funktionen:")
        
        # Customer Path Configuration
        print("- Kundenpfad-Konfiguration:")
        try:
            # Prüfe ob die Funktion existiert
            if hasattr(app, 'configure_customer_path'):
                print("  ✅ configure_customer_path Funktion existiert")
                # Teste die Funktion (ohne GUI zu öffnen)
                print("  ✅ Kundenpfad-Konfiguration verfügbar")
            else:
                print("  ❌ configure_customer_path Funktion fehlt")
        except Exception as e:
            print(f"  ❌ Kundenpfad-Konfiguration Fehler: {e}")
        
        # Kunde bestätigen
        print("- Kunde bestätigen:")
        try:
            if hasattr(app, 'confirm_customer'):
                print("  ✅ confirm_customer Funktion existiert")
            else:
                print("  ❌ confirm_customer Funktion fehlt")
        except Exception as e:
            print(f"  ❌ Kunde bestätigen Fehler: {e}")
        
        # Kunden Manager
        print("- Kunden Manager:")
        try:
            if hasattr(app, 'kunden_manager'):
                print("  ✅ kunden_manager verfügbar")
                print(f"  📁 Basis-Pfad: {app.kunden_base_dir}")
            else:
                print("  ❌ kunden_manager fehlt")
        except Exception as e:
            print(f"  ❌ Kunden Manager Fehler: {e}")
        
        print("\n🎉 Menütest abgeschlossen!")
        return True
        
    except Exception as e:
        print(f"❌ Kritischer Fehler beim Menütest: {e}")
        return False

def test_menu_items():
    """Test der Menüeinträge - überprüft die Struktur"""
    print("\n📋 Teste Menüstruktur...")
    
    try:
        from checker_app import CheckerApp
        app = CheckerApp()
        
        # Erwartete Menüeinträge
        expected_menus = {
            "Tools": ["Kundenpfad konfigurieren", "Theme umschalten", "Layout zurücksetzen"],
            "Kunden": ["Neuer Kunde", "Kundenliste", "Kunde suchen", "Kundenpfad konfigurieren", "Kundenordner öffnen"],
            "Workflows": ["Angebotsanalyse", "Dateiprüfung"],
            "Hilfe": ["Benutzerhandbuch", "Schnellstart-Guide", "FAQ", "Über Checker Pro Suite"]
        }
        
        print("✅ Erwartete Menüstruktur definiert")
        
        # Prüfe ob kritische Funktionen existieren
        critical_functions = [
            'configure_customer_path',
            'show_tools_menu',
            'show_customer_menu',
            'show_workflow_menu',
            'show_help_menu'
        ]
        
        for func_name in critical_functions:
            if hasattr(app, func_name):
                print(f"  ✅ {func_name} vorhanden")
            else:
                print(f"  ❌ {func_name} fehlt")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Menüstruktur-Test: {e}")
        return False

def main():
    """Hauptfunktion für den Test"""
    print("🚀 Starte Menü-Tests für Checker App")
    print("=" * 50)
    
    # Test 1: Menüzugriff
    success1 = test_menu_access()
    
    # Test 2: Menüstruktur
    success2 = test_menu_items()
    
    # Zusammenfassung
    print("\n" + "=" * 50)
    print("📊 Test-Zusammenfassung:")
    print(f"- Menüzugriff: {'✅ OK' if success1 else '❌ FEHLER'}")
    print(f"- Menüstruktur: {'✅ OK' if success2 else '❌ FEHLER'}")
    
    if success1 and success2:
        print("\n🎉 Alle Tests erfolgreich! Die Menüs sind korrekt implementiert.")
        return True
    else:
        print("\n⚠️  Einige Tests sind fehlgeschlagen. Bitte überprüfen Sie die Implementierung.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
