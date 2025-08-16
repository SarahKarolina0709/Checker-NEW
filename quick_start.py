#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Quick Start Menu - Einfacher Workflow-Launcher
===============================================

Schneller Zugang zu allen wichtigen Checker-Anwendungen.
"""

import subprocess
import sys
import os

def show_menu():
    """Zeige verfügbare Anwendungen"""
    print("\n" + "="*60)
    print("🚀 TRANSLATION QUALITY CHECKER - QUICK START")
    print("="*60)
    print()
    print("Verfügbare Anwendungen:")
    print()
    print("1. 📊 Quality GUI Main App (Empfohlen)")
    print("   • Verbesserte Kundenauswahl")
    print("   • Upload-Workflows") 
    print("   • Qualitätsprüfung")
    print()
    print("2. 🏠 Welcome Screen (Modulare Übersicht)")
    print("   • Projekt-Dashboard")
    print("   • Datei-Management")
    print("   • Calendar-System")
    print()
    print("3. 🔧 Modular GUI (Alternative)")
    print("   • Modulare Architektur")
    print("   • Erweiterte Features")
    print()
    print("4. 📋 Legacy GUI (Klassisch)")
    print("   • Original-Interface")
    print("   • Bewährte Funktionen")
    print()
    print("0. ❌ Beenden")
    print()

def start_application(choice):
    """Starte gewählte Anwendung"""
    apps = {
        '1': 'quality_gui_main_app.py',
        '2': 'start_welcome.py', 
        '3': 'modern_translation_quality_gui_modular.py',
        '4': 'modern_translation_quality_gui.py'
    }
    
    if choice in apps:
        app_file = apps[choice]
        if os.path.exists(app_file):
            print(f"\n🚀 Starte {app_file}...")
            try:
                subprocess.run([sys.executable, app_file], check=True)
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Fehler beim Starten: {e}")
                return False
        else:
            print(f"❌ Datei nicht gefunden: {app_file}")
            return False
    else:
        print("❌ Ungültige Auswahl")
        return False

def main():
    """Hauptfunktion"""
    while True:
        show_menu()
        choice = input("Wählen Sie eine Option (0-4): ").strip()
        
        if choice == '0':
            print("\n👋 Auf Wiedersehen!")
            break
        elif choice in ['1', '2', '3', '4']:
            success = start_application(choice)
            if success:
                print("\n✅ Anwendung gestartet!")
                break
            else:
                input("\nDrücken Sie Enter um fortzufahren...")
        else:
            print("❌ Ungültige Eingabe. Bitte wählen Sie 0-4.")
            input("\nDrücken Sie Enter um fortzufahren...")

if __name__ == "__main__":
    main()
