#!/usr/bin/env python3
"""
Quick Commands für CustomerSectionComplete
Schnelle Befehle zum Testen und Aufrufen der Customer View
"""

import subprocess
import sys
import os
from pathlib import Path

def run_checker_app():
    """Starte die CheckerApp direkt"""
    print("🚀 Starte CheckerApp...")
    try:
        subprocess.run([sys.executable, "checker_app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Starten der CheckerApp: {e}")
    except FileNotFoundError:
        print("❌ checker_app.py nicht gefunden!")

def run_live_test():
    """Starte den Live Test"""
    print("🧪 Starte Live Test...")
    try:
        subprocess.run([sys.executable, "live_test_customer_section.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Starten des Live Tests: {e}")
    except FileNotFoundError:
        print("❌ live_test_customer_section.py nicht gefunden!")

def run_demo():
    """Starte die Aufruf-Demo"""
    print("🎯 Starte Aufruf-Demo...")
    try:
        subprocess.run([sys.executable, "demo_customer_section_calls.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Starten der Demo: {e}")
    except FileNotFoundError:
        print("❌ demo_customer_section_calls.py nicht gefunden!")

def check_integration():
    """Prüfe die Integration"""
    print("🔍 Prüfe CustomerSectionComplete Integration...")
    
    # Check if files exist
    files_to_check = [
        "checker_app.py",
        "welcome_screen_components/customer_section_complete.py",
        "view_stack.py"
    ]
    
    all_present = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} gefunden")
        else:
            print(f"❌ {file_path} nicht gefunden")
            all_present = False
    
    if all_present:
        print("\n✅ Alle erforderlichen Dateien sind vorhanden!")
        
        # Check integration in checker_app.py
        try:
            with open("checker_app.py", "r", encoding="utf-8") as f:
                content = f.read()
                
            if "CustomerSectionComplete" in content:
                print("✅ CustomerSectionComplete ist in checker_app.py integriert")
            else:
                print("❌ CustomerSectionComplete nicht in checker_app.py gefunden")
                
            if "customer_management" in content:
                print("✅ 'customer_management' View-ID gefunden")
            else:
                print("❌ 'customer_management' View-ID nicht gefunden")
                
        except Exception as e:
            print(f"❌ Fehler beim Prüfen der Integration: {e}")
    else:
        print("\n❌ Nicht alle erforderlichen Dateien sind vorhanden!")

def show_usage():
    """Zeige Verwendungshinweise"""
    print("🎯 CustomerSectionComplete - Quick Commands")
    print("=" * 50)
    print()
    print("📋 Verfügbare Aufruf-Methoden:")
    print("1. app.views.show('customer_management')")
    print("2. app.show_customer_menu()")
    print("3. app.show_customer_section_complete()")
    print("4. ctk.CTkButton(..., command=lambda: app.views.show('customer_management'))")
    print()
    print("🚀 Quick Commands:")
    print("python quick_commands.py app       - Starte CheckerApp")
    print("python quick_commands.py test      - Starte Live Test")
    print("python quick_commands.py demo      - Starte Aufruf-Demo")
    print("python quick_commands.py check     - Prüfe Integration")
    print("python quick_commands.py help      - Zeige diese Hilfe")
    print()
    print("💡 Empfehlung:")
    print("1. Führen Sie 'check' aus, um die Integration zu prüfen")
    print("2. Starten Sie 'app' und klicken Sie auf 'Kunden' im Menü")
    print("3. Alternativ führen Sie 'test' aus für detaillierte Tests")

def main():
    """Hauptfunktion für Quick Commands"""
    if len(sys.argv) < 2:
        show_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "app":
        run_checker_app()
    elif command == "test":
        run_live_test()
    elif command == "demo":
        run_demo()
    elif command == "check":
        check_integration()
    elif command in ["help", "-h", "--help"]:
        show_usage()
    else:
        print(f"❌ Unbekannter Befehl: {command}")
        print("Verwenden Sie 'help' für verfügbare Befehle.")

if __name__ == "__main__":
    main()
