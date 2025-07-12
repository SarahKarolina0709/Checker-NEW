#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Welcome Screen Test - Umfassender Test der Welcome-Screen-Funktionalität
"""

import sys
import os
import traceback
import tkinter as tk
from tkinter import messagebox

# Pfad zur Checker-App hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_welcome_screen_import():
    """Test des Imports der Welcome-Screen-Komponenten"""
    print("=" * 60)
    print("WELCOME SCREEN TEST - Import-Prüfung")
    print("=" * 60)
    
    try:
        # Test 1: Ultra Modern Welcome Screen Import
        print("✓ Test 1: UltraModernWelcomeScreen Import...")
        from ultra_modern_welcome_screen_v2 import UltraModernWelcomeScreen, HoverCard
        print("  ✓ UltraModernWelcomeScreen erfolgreich importiert")
        print("  ✓ HoverCard erfolgreich importiert")
        
        # Test 2: Checker App Import
        print("✓ Test 2: CheckerApp Import...")
        from checker_app import CheckerApp
        print("  ✓ CheckerApp erfolgreich importiert")
        
        # Test 3: Abhängigkeiten prüfen
        print("✓ Test 3: Abhängigkeiten prüfen...")
        import customtkinter as ctk
        from PIL import Image, ImageTk
        from tkinterdnd2 import TkinterDnD
        print("  ✓ CustomTkinter verfügbar")
        print("  ✓ PIL/Pillow verfügbar")
        print("  ✓ TkinterDnD verfügbar")
        
        return True
        
    except Exception as e:
        print(f"❌ Import-Fehler: {e}")
        traceback.print_exc()
        return False

def test_welcome_screen_standalone():
    """Test des Welcome-Screens als eigenständige Komponente"""
    print("\n" + "=" * 60)
    print("WELCOME SCREEN TEST - Standalone-Test")
    print("=" * 60)
    
    try:
        # Mock-App für Testing
        class MockApp:
            def __init__(self):
                self.root = None
                self.logger = None
                
            def get_icon(self, icon_name, size=(24, 24)):
                """Mock Icon-Funktion"""
                return None  # Simuliert fehlende Icons
            
            def handle_workflow_start(self, workflow_type, customer_data):
                """Mock Workflow-Handler"""
                print(f"Mock: Workflow '{workflow_type}' gestartet mit Daten: {customer_data}")
        
        # Test-Root erstellen
        root = tk.Tk()
        root.title("Welcome Screen Standalone Test")
        root.geometry("1200x800")
        root.withdraw()  # Verstecken für jetzt
        
        # Mock-App erstellen
        mock_app = MockApp()
        mock_app.root = root
        
        # Welcome Screen erstellen
        print("✓ Erstelle Welcome Screen...")
        from ultra_modern_welcome_screen_v2 import UltraModernWelcomeScreen
        
        welcome_screen = UltraModernWelcomeScreen(
            master=root,
            app=mock_app,
            app_callback=mock_app.handle_workflow_start
        )
        
        print("  ✓ Welcome Screen erfolgreich erstellt")
        print("  ✓ UI-Komponenten initialisiert")
        
        # Test der Methoden
        print("✓ Teste Welcome Screen Methoden...")
        
        # Test safe_get_icon
        if hasattr(welcome_screen, 'safe_get_icon'):
            icon, text = welcome_screen.safe_get_icon('test_icon', fallback_text="🔧")
            print(f"  ✓ safe_get_icon funktioniert: icon={icon}, text='{text}'")
        
        # Test validate_customer_inputs
        if hasattr(welcome_screen, 'validate_customer_inputs'):
            welcome_screen.validate_customer_inputs()
            print("  ✓ validate_customer_inputs funktioniert")
        
        # Test theme toggle
        if hasattr(welcome_screen, 'toggle_theme'):
            original_theme = welcome_screen.current_theme
            welcome_screen.toggle_theme()
            print(f"  ✓ toggle_theme funktioniert: {original_theme} -> {welcome_screen.current_theme}")
        
        print("✓ Alle Tests erfolgreich!")
        
        # Cleanup
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Standalone-Test-Fehler: {e}")
        traceback.print_exc()
        return False

def test_welcome_screen_integration():
    """Test der Integration mit der Hauptanwendung"""
    print("\n" + "=" * 60)
    print("WELCOME SCREEN TEST - Integration-Test")
    print("=" * 60)
    
    try:
        print("✓ Teste Integration mit CheckerApp...")
        
        # Teste nur die Klassen-Definitionen und Methoden-Signaturen
        from checker_app import CheckerApp
        from ultra_modern_welcome_screen_v2 import UltraModernWelcomeScreen
        
        # Prüfe erforderliche Methoden in CheckerApp
        required_methods = [
            'get_icon', 'handle_workflow_start', 'show_welcome_screen',
            'clear_main_container', 'register_persistent_button'
        ]
        
        for method in required_methods:
            if hasattr(CheckerApp, method):
                print(f"  ✓ CheckerApp.{method} verfügbar")
            else:
                print(f"  ❌ CheckerApp.{method} FEHLT")
                return False
        
        # Prüfe erforderliche Methoden in UltraModernWelcomeScreen
        required_welcome_methods = [
            'setup_ui', 'safe_get_icon', 'validate_customer_inputs',
            'toggle_theme', 'create_new_customer', 'reset_customer_fields'
        ]
        
        for method in required_welcome_methods:
            if hasattr(UltraModernWelcomeScreen, method):
                print(f"  ✓ UltraModernWelcomeScreen.{method} verfügbar")
            else:
                print(f"  ❌ UltraModernWelcomeScreen.{method} FEHLT")
                return False
        
        print("✓ Integration-Test erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ Integration-Test-Fehler: {e}")
        traceback.print_exc()
        return False

def test_workflow_mappings():
    """Test der Workflow-Mappings und Routing"""
    print("\n" + "=" * 60)
    print("WELCOME SCREEN TEST - Workflow-Mappings")
    print("=" * 60)
    
    try:
        from ultra_modern_welcome_screen_v2 import UltraModernWelcomeScreen
        
        # Test der Workflow-Methoden
        workflow_methods = [
            'on_new_angebot', 'on_new_auftrag', 
            'on_new_korrektur', 'on_export'
        ]
        
        print("✓ Prüfe Workflow-Methoden...")
        for method in workflow_methods:
            if hasattr(UltraModernWelcomeScreen, method):
                print(f"  ✓ {method} verfügbar")
            else:
                print(f"  ❌ {method} FEHLT")
                return False
        
        # Test der Tool-Methoden
        tool_methods = [
            'open_file_dialog', 'open_folder_dialog', 'show_export_options',
            'show_settings', 'show_help', 'show_about'
        ]
        
        print("✓ Prüfe Tool-Methoden...")
        for method in tool_methods:
            if hasattr(UltraModernWelcomeScreen, method):
                print(f"  ✓ {method} verfügbar")
            else:
                print(f"  ❌ {method} FEHLT")
                return False
        
        print("✓ Workflow-Mappings-Test erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ Workflow-Mappings-Test-Fehler: {e}")
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Führt alle Tests aus"""
    print("WELCOME SCREEN - UMFASSENDER TEST")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"Arbeitsverzeichnis: {os.getcwd()}")
    print()
    
    tests = [
        ("Import-Test", test_welcome_screen_import),
        ("Standalone-Test", test_welcome_screen_standalone),
        ("Integration-Test", test_welcome_screen_integration),
        ("Workflow-Mappings-Test", test_workflow_mappings)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Kritischer Fehler in {test_name}: {e}")
            results.append((test_name, False))
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("TEST-ZUSAMMENFASSUNG")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ BESTANDEN" if result else "❌ FEHLGESCHLAGEN"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Gesamt: {len(results)} Tests")
    print(f"Bestanden: {passed}")
    print(f"Fehlgeschlagen: {failed}")
    
    if failed == 0:
        print("\n🎉 ALLE TESTS ERFOLGREICH! Welcome Screen ist bereit.")
    else:
        print(f"\n⚠️  {failed} Tests fehlgeschlagen. Überprüfung erforderlich.")
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest durch Benutzer abgebrochen.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Kritischer Fehler: {e}")
        traceback.print_exc()
        sys.exit(1)
