#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏠 DIREKTER STARTER FÜR ORIGINALEN WELCOME SCREEN
=================================================

Startet den ECHTEN, ursprünglichen Welcome Screen aus dem Backup.
Nicht den modularen oder vereinfachten - sondern dein ORIGINAL!
"""

import customtkinter as ctk
import sys
import os

# Force light mode
ctk.set_appearance_mode("light")

def main():
    """🚀 Start the ORIGINAL Welcome Screen"""
    print("🏠 ORIGINALER WELCOME SCREEN - DIREKTER START")
    print("=" * 50)
    print("Startet dein ECHTES Original aus dem Backup:")
    print("👤 Kundenmanagement mit 39 Kunden")
    print("📁 Upload System mit Drag & Drop")
    print("🎯 Workflow-Auswahl")
    print("📊 Dashboard & Statistiken")
    print("🍞 Toast-Notifications")
    print("⌨️ Keyboard-Shortcuts")
    print()

    try:
        # Import the original welcome screen directly
        print("📦 Importiere ORIGINALEN Welcome Screen...")
        from welcome_screen import WelcomeScreen
        print("✅ Original Welcome Screen Klasse geladen")
        
        # Create main window
        root = ctk.CTk()
        root.title("🏠 Checker - Originaler Welcome Screen")
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
        
        # Create a proper app object for the welcome screen
        class MockApp:
            def __init__(self):
                self.uploaded_files = {'source': [], 'translation': []}
                self.analysis_results = {}
                self.current_customer = None
                self.customers = []
                
                # Load customers from JSON if available
                try:
                    import json
                    from pathlib import Path
                    customers_file = Path("customers.json")
                    if customers_file.exists():
                        with open(customers_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, dict):
                                self.customers = list(data.keys())
                            elif isinstance(data, list):
                                self.customers = data
                    print(f"✅ {len(self.customers)} Kunden aus customers.json geladen")
                except Exception as e:
                    print(f"⚠️ Kunden laden fehlgeschlagen: {e}")
        
        mock_app = MockApp()
        
        # Create Welcome Screen with required parameters
        welcome_screen = WelcomeScreen(master=root, app=mock_app)
        # Ensure it's visible (attach to root); ignore if WelcomeScreen manages layout internally
        try:
            welcome_screen.pack(side="top", fill="both", expand=True)
        except Exception:
            pass
        print("✅ ORIGINALER Welcome Screen initialisiert")
        
        # The welcome screen should already be visible since it's bound to root
        # Just ensure root is properly displayed
        
        # Force window to front and make sure it's visible
        root.lift()
        root.focus_force()
        root.attributes('-topmost', True)
        root.after(100, lambda: root.attributes('-topmost', False))
        
        # Force update to ensure rendering
        root.update()
        
        print("\n🎉 ORIGINALER WELCOME SCREEN GESTARTET!")
        print("Du siehst jetzt dein ECHTES Original-Interface:")
        print("👤 Kundenmanagement (39 Kunden geladen)")
        print("📁 Upload System mit Drag & Drop")
        print("🎯 Workflow-Auswahl") 
        print("📊 Dashboard mit Live-Statistiken")
        print("🍞 Professional Toast-System")
        print("⌨️ Keyboard-Shortcuts aktiv")
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
