#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏠 ORIGINALER WELCOME SCREEN GUI STARTER
=======================================

Startet den echten, originalen Welcome Screen mit:
👤 Kundenmanagement (links)
📁 Upload System (mitte)  
🎯 Workflow-Auswahl (rechts)

Dieser ist aus dem backup_ultimate wiederhergestellt.
"""

import customtkinter as ctk
import sys
import os
from welcome_screen import WelcomeScreen

# Force light mode
ctk.set_appearance_mode("light")

def main():
    """🚀 Start the Original Welcome Screen GUI"""
    print("🏠 CHECKER - ORIGINALER WELCOME SCREEN")
    print("=" * 50)
    print("Starte dein ECHTES Hauptinterface aus dem Backup:")
    print("👤 Kundenmanagement")
    print("📁 Upload System mit Drag & Drop") 
    print("🎯 Workflow-Auswahl (alle Prüfungsworkflows)")
    print("📊 Statistiken & Dashboard")
    print("🍞 Toast-Notifications")
    print("⌨️  Keyboard-Shortcuts")
    print()

    try:
        # Import the consolidated welcome screen class
        print("📦 Importiere konsolidierten Welcome Screen aus welcome_screen.py...")
        print("✅ Welcome Screen Klasse geladen")

        # Create main window
        root = ctk.CTk()
        # Kein Emoji im UI-Titel (No-Icons-Policy)
        root.title("Checker - Original Welcome Screen")
        root.geometry("1600x1000")
        root.minsize(1000, 700)

        # Center window
        root.update_idletasks()
        width = 1600
        height = 1000
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")

        # Configure colors
        root.configure(fg_color="#FFFFFF")

        print("✅ Hauptfenster erstellt (1600x1000)")

        # Create a mock app object for the welcome screen
        class MockApp:
            def __init__(self):
                self.uploaded_files = {'source': [], 'translation': []}
                self.analysis_results = {}
                self.current_customer = None

        mock_app = MockApp()

        # Create Welcome Screen with required app parameter
        welcome_screen = WelcomeScreen(root, mock_app)
        # Attach to root to ensure visibility (avoid white screen)
        try:
            welcome_screen.pack(side="top", fill="both", expand=True)
        except Exception:
            # If WelcomeScreen manages its own layout, ignore
            pass
        print("✅ Original Welcome Screen initialisiert")

        print("\n🎉 ORIGINAL WELCOME SCREEN ERFOLGREICH GESTARTET!")
        print("Du siehst jetzt deine ECHTEN drei Hauptbereiche:")
        print("👤 Kundenmanagement (links) - Kunden erstellen, auswählen, verwalten")
        print("📁 Upload System (mitte) - Drag & Drop, Dateiverwaltung")
        print("🎯 Workflow-Auswahl (rechts) - Alle Prüfungsworkflows")
        print()
        print("📊 Plus: Dashboard, Statistiken, Toast-Notifications")
        print("⌨️  Keyboard-Shortcuts aktiv")
        print("🎨 Professional Design mit Icon-freier Oberfläche")
        print("\nSchließe mit Alt+F4 oder dem X-Button")

        # Start GUI loop
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Fehler beim Start: {e}")
        import traceback
        traceback.print_exc()
        input("Drücke Enter zum Beenden...")

if __name__ == "__main__":
    main()
