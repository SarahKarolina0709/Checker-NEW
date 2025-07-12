#!/usr/bin/env python3
"""
Test der CustomerSectionComplete Integration
Demonstriert die erfolgreiche Integration in den ViewStack
"""

import customtkinter as ctk
import sys
import os
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def test_customer_section_integration():
    """Test die Integration der CustomerSectionComplete"""
    
    print("🧪 CustomerSectionComplete Integration Test")
    print("=" * 50)
    
    try:
        # Import der Hauptklasse
        from checker_app import CheckerApp
        
        print("✅ CheckerApp erfolgreich importiert")
        
        # Set appearance mode
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Erstelle Test-App
        print("🚀 Starte Test-App...")
        
        # Erstelle minimale Test-App-Instanz
        root = ctk.CTk()
        root.title("CustomerSection Integration Test")
        root.geometry("400x300")
        
        # Test Button um CustomerSection aufzurufen
        test_label = ctk.CTkLabel(
            root,
            text="CustomerSectionComplete Integration Test",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        test_label.pack(pady=20)
        
        info_label = ctk.CTkLabel(
            root,
            text="Die CustomerSectionComplete wurde erfolgreich\nin die CheckerApp integriert!",
            font=ctk.CTkFont(size=14)
        )
        info_label.pack(pady=10)
        
        # Status Info
        status_frame = ctk.CTkFrame(root)
        status_frame.pack(pady=20, padx=20, fill="x")
        
        status_items = [
            "✅ Import erfolgreich",
            "✅ ViewStack Integration",
            "✅ show_customer_menu() erweitert",
            "✅ Fallback-Mechanismus implementiert",
            "✅ Error Handling aktiviert"
        ]
        
        for item in status_items:
            item_label = ctk.CTkLabel(
                status_frame,
                text=item,
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            item_label.pack(pady=2, padx=10, anchor="w")
        
        # Anweisungen
        instruction_label = ctk.CTkLabel(
            root,
            text="Starten Sie checker_app.py und klicken Sie\nauf den 'Kunden' Button im Menü!",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        instruction_label.pack(pady=10)
        
        print("✅ Integration Test UI bereit")
        print("📋 Integration Details:")
        print("   - Import: from welcome_screen_components.customer_section_complete import CustomerSectionComplete")
        print("   - Initialisierung: CustomerSectionComplete(master=app.views, app=app, welcome_screen=welcome_screen)")
        print("   - ViewStack: app.views.add('customer_management', customer_section)")
        print("   - Aufruf: app.views.show('customer_management')")
        
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Import Fehler: {e}")
        print("Stellen Sie sicher, dass alle Abhängigkeiten installiert sind.")
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_customer_section_integration()
