#!/usr/bin/env python3
"""
Debug-Version der CheckerApp - Identifiziert wo genau das Problem liegt
"""

import sys
import os

# Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports_step_by_step():
    """Testet jeden Import einzeln"""
    print("🔍 Teste Imports Schritt für Schritt...")
    
    try:
        print("Step 1: nuclear_scaling_killer...")
        import nuclear_scaling_killer
        print("✅ nuclear_scaling_killer - OK")
        
        print("Step 2: Standard libraries...")
        import datetime
        import gc
        import json
        import logging
        import os
        import platform
        import subprocess
        import sys
        import threading
        import traceback
        import tkinter as tk
        from tkinter import filedialog, messagebox, simpledialog
        from typing import Optional
        print("✅ Standard libraries - OK")
        
        print("Step 3: customtkinter...")
        import customtkinter as ctk
        print("✅ customtkinter - OK")
        
        print("Step 4: psutil...")
        import psutil
        print("✅ psutil - OK")
        
        print("Step 5: PIL...")
        from PIL import Image, ImageTk
        print("✅ PIL - OK")
        
        print("Step 6: tkinterdnd2...")
        from tkinterdnd2 import TkinterDnD
        print("✅ tkinterdnd2 - OK")
        
        print("Step 7: error_handlers...")
        try:
            from error_handlers import CrashRecoveryManager, EnhancedLogger, ErrorMonitor
            print("✅ error_handlers - OK")
        except ImportError as e:
            print(f"⚠️ error_handlers - NICHT VERFÜGBAR: {e}")
        
        print("Step 8: fluent_icons_manager...")
        from fluent_icons_manager import FluentIconManager
        print("✅ fluent_icons_manager - OK")
        
        print("Step 9: kunden_manager...")
        from kunden_manager import KundenManager
        print("✅ kunden_manager - OK")
        
        print("Step 10: ui_theme...")
        from ui_theme import UITheme
        print("✅ ui_theme - OK")
        
        print("Step 11: ultra_modern_welcome_screen_simplified...")
        try:
            from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen
            print("✅ ultra_modern_welcome_screen_simplified - OK")
        except ImportError as e:
            print(f"⚠️ ultra_modern_welcome_screen_simplified - NICHT VERFÜGBAR: {e}")
        
        print("\n🎉 Alle Imports erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ Import-Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_checker_app_class():
    """Testet nur die CheckerApp-Klasse ohne Instanziierung"""
    print("\n🔍 Teste CheckerApp-Klasse...")
    
    try:
        print("Importing CheckerApp class...")
        # Importiere nur die Klasse, erstelle keine Instanz
        import checker_app
        print("✅ CheckerApp-Modul importiert")
        
        # Prüfe ob die Klasse existiert
        if hasattr(checker_app, 'CheckerApp'):
            print("✅ CheckerApp-Klasse gefunden")
            
            # Prüfe wichtige Methoden
            required_methods = [
                '__init__',
                'setup_application',
                'setup_ui',
                '_setup_workflow_routes',
                'on_closing'
            ]
            
            missing_methods = []
            for method in required_methods:
                if hasattr(checker_app.CheckerApp, method):
                    print(f"✅ {method} - vorhanden")
                else:
                    missing_methods.append(method)
                    print(f"❌ {method} - FEHLT")
            
            if missing_methods:
                print(f"⚠️ Fehlende Methoden: {missing_methods}")
                return False
            else:
                print("✅ Alle erforderlichen Methoden vorhanden")
                return True
        else:
            print("❌ CheckerApp-Klasse nicht gefunden")
            return False
            
    except Exception as e:
        print(f"❌ Fehler beim Testen der CheckerApp-Klasse: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Hauptfunktion"""
    print("🚀 Starte umfassenden Debug-Test...\n")
    
    # Test 1: Imports
    imports_ok = test_imports_step_by_step()
    
    # Test 2: CheckerApp-Klasse
    class_ok = test_checker_app_class()
    
    # Zusammenfassung
    print("\n" + "="*50)
    print("📊 Debug-Test Zusammenfassung:")
    print(f"- Imports: {'✅ OK' if imports_ok else '❌ FEHLER'}")
    print(f"- CheckerApp-Klasse: {'✅ OK' if class_ok else '❌ FEHLER'}")
    
    if imports_ok and class_ok:
        print("\n🎉 Alle Tests erfolgreich!")
        print("💡 Das Problem liegt wahrscheinlich in der Instanziierung oder im Startup-Prozess.")
        
        # Empfehlung
        print("\n🔧 Empfehlung:")
        print("- Verwenden Sie die vereinfachte Version: python checker_app_simple.py")
        print("- Oder deaktivieren Sie das Splash-Screen-System temporär")
        
        return True
    else:
        print("\n⚠️ Probleme gefunden!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
