#!/usr/bin/env python3
# DEPRECATED: Nutze 'start_checker.py --welcome' oder '--menu'.
# -*- coding: utf-8 -*-
"""
🏠 WELCOME SCREEN GUI STARTER
============================

Startet das echte Welcome Screen Interface - dein Hauptstartbildschirm
mit den drei Containern: Kundenmanagement, Upload und Workflow-Auswahl.
"""

import customtkinter as ctk
import sys
import os

# Force light mode
ctk.set_appearance_mode("light")

try:
    from welcome_screen import WelcomeScreen
    print("✅ Welcome Screen Module importiert")
except ImportError as e:
    print(f"❌ Welcome Screen Import-Fehler: {e}")
    sys.exit(1)

def main():
    """🚀 Start the Welcome Screen GUI"""
    print("WELCOME SCREEN STARTER (Deprecated – nutze start_checker.py --welcome)")
    print("=" * 50)
    print("Starte dein Hauptinterface mit:")
    print("👤 Kundenmanagement")
    print("📁 Upload System") 
    print("🎯 Workflow-Auswahl (Prüfungsworkflows)")
    print()

    try:
        # Create main window
        root = ctk.CTk()
        root.title("🏠 Checker - Welcome Screen")
        root.geometry("1400x900")
        root.minsize(800, 600)
        
        # Center window
        root.update_idletasks()
        width = root.winfo_reqwidth()
        height = root.winfo_reqheight()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configure colors
        root.configure(fg_color="#FFFFFF")
        
        print("✅ Hauptfenster erstellt")
        
        # Create Welcome Screen
        welcome_screen = WelcomeScreen(root)
        print("✅ Welcome Screen initialisiert")
        
        # Show Welcome Screen
        welcome_screen.show()
        print("✅ Welcome Screen angezeigt")
        
        print("\n🎉 WELCOME SCREEN ERFOLGREICH GESTARTET!")
        print("Du siehst jetzt deine drei Hauptbereiche:")
        print("👤 Kundenmanagement (links)")
        print("📁 Upload System (mitte)")
        print("🎯 Workflow-Auswahl (rechts)")
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
