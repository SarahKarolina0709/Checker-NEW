#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 WELCOME SCREEN STANDALONE TEST
================================

Testet das Welcome Screen System als eigenständige Anwendung.
Das normale welcome_screen.py ist als Modul konzipiert.
"""

import customtkinter as ctk
from welcome_screen import WelcomeScreen

def main():
    """Start Welcome Screen Test"""
    print("🏠 WELCOME SCREEN STANDALONE TEST")
    print("=" * 40)
    
    try:
        # Create main window
        root = ctk.CTk()
        root.title("Checker Welcome Screen Test")
        root.geometry("1200x800")
        root.minsize(800, 600)
        
        print("✅ Root window created")
        
        # Create welcome screen
        welcome = WelcomeScreen(root)
        print("✅ Welcome screen initialized")
        
        # Show welcome screen
        welcome.show()
        print("✅ Welcome screen displayed")
        
        print("\n🚀 WELCOME SCREEN LÄUFT!")
        print("Schließe das Fenster um den Test zu beenden.")
        
        # Start the application
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n👋 Test beendet durch Benutzer")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
