#!/usr/bin/env python3
"""
Debug-Test für den Kalender-Dialog
Identifiziert das Problem mit der Kalender-Anzeige
"""

import os
import sys
import customtkinter as ctk
from datetime import datetime, timedelta
import calendar
from tkinter import messagebox
import traceback

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the required modules
class MockUITheme:
    COLOR_PRIMARY = "#3B82F6"
    COLOR_SECONDARY = "#6B7280"
    COLOR_SUCCESS = "#10B981"
    COLOR_SUCCESS_HOVER = "#059669"
    COLOR_SURFACE = "#F8FAFC"
    COLOR_CARD = "#FFFFFF"
    COLOR_TEXT_PRIMARY = "#1F2937"
    COLOR_TEXT_SECONDARY = "#6B7280"
    COLOR_TEXT_ON_PRIMARY = "#FFFFFF"
    COLOR_PRIMARY_SURFACE = "#DBEAFE"
    COLOR_PRIMARY_HOVER = "#2563EB"
    COLOR_BG_SECONDARY = "#F1F5F9"
    COLOR_CONTAINER_CUSTOMER = "#EBF8FF"
    CONTAINER_STYLE_CUSTOMER = {"fg_color": "#FFFFFF", "corner_radius": 8}
    SPACING_L = 15
    SPACING_M = 10
    SPACING_XL = 20
    SPACING_XXL = 25
    FONT_FAMILY_UI = "Segoe UI"
    BUTTON_STYLE_PRIMARY = {"fg_color": "#3B82F6", "hover_color": "#2563EB"}
    BUTTON_STYLE_SECONDARY = {"fg_color": "#6B7280", "hover_color": "#4B5563"}
    INPUT_STYLE_MODERN = {"border_color": "#D1D5DB", "fg_color": "#FFFFFF"}
    CORNER_RADIUS = 8

class MockLogger:
    def info(self, message):
        print(f"[INFO] {message}")
    
    def error(self, message):
        print(f"[ERROR] {message}")
        
    def warning(self, message):
        print(f"[WARNING] {message}")
    
    def debug(self, message):
        print(f"[DEBUG] {message}")

def test_calendar_dialog():
    """Test den Kalender-Dialog direkt"""
    
    def show_test_dialog():
        """Zeigt einen Test-Dialog für Upload-Details"""
        try:
            print("Creating test dialog...")
            
            # Test-Dialog erstellen
            dialog = ctk.CTkToplevel(app)
            dialog.title("Test Upload-Details")
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            
            print("Dialog created, setting properties...")
            
            # Dialog zentrieren und fokussieren
            dialog.transient(app)
            dialog.grab_set()
            
            # Header
            header_frame = ctk.CTkFrame(dialog, fg_color=MockUITheme.COLOR_PRIMARY)
            header_frame.pack(fill="x", padx=10, pady=10)
            
            header_label = ctk.CTkLabel(
                header_frame,
                text="📅 Test Dialog",
                font=ctk.CTkFont(family=MockUITheme.FONT_FAMILY_UI, size=16, weight="bold"),
                text_color=MockUITheme.COLOR_TEXT_ON_PRIMARY
            )
            header_label.pack(pady=10)
            
            # Content
            content_frame = ctk.CTkFrame(dialog, fg_color=MockUITheme.COLOR_SURFACE)
            content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            # Test-Inhalt
            test_label = ctk.CTkLabel(
                content_frame,
                text="Dies ist ein Test-Dialog.\nWenn Sie das sehen, funktioniert die Dialog-Erstellung.",
                font=ctk.CTkFont(family=MockUITheme.FONT_FAMILY_UI, size=12),
                justify="center"
            )
            test_label.pack(pady=20)
            
            # Test Upload-Item
            upload_frame = ctk.CTkFrame(content_frame, fg_color=MockUITheme.COLOR_CARD)
            upload_frame.pack(fill="x", padx=10, pady=10)
            
            upload_label = ctk.CTkLabel(
                upload_frame,
                text="📁 Test Upload: Mustermann GmbH\n🕐 14:30\n📄 2 Dateien: test1.pdf, test2.docx",
                font=ctk.CTkFont(family=MockUITheme.FONT_FAMILY_UI, size=11),
                justify="left"
            )
            upload_label.pack(pady=10, padx=10)
            
            # Schließen-Button
            close_btn = ctk.CTkButton(
                dialog,
                text="Schließen",
                command=dialog.destroy,
                **MockUITheme.BUTTON_STYLE_SECONDARY
            )
            close_btn.pack(pady=10)
            
            # Dialog fokussieren
            dialog.focus()
            dialog.lift()
            
            print("Dialog setup complete!")
            
        except Exception as e:
            print(f"Error creating dialog: {e}")
            traceback.print_exc()
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Dialogs: {e}")
    
    def test_calendar_functionality():
        """Test die Kalender-Funktionalität"""
        try:
            print("Testing calendar functionality...")
            
            # Test-Daten
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            upload_data = {
                today: [
                    {
                        'customer': 'Mustermann GmbH',
                        'files': ['angebot_2025.pdf', 'vertrag_entwurf.docx'],
                        'time': '14:30'
                    }
                ],
                yesterday: [
                    {
                        'customer': 'TechCorp AG',
                        'files': ['logo_varianten.zip'],
                        'time': '16:45'
                    }
                ]
            }
            
            print(f"Test data created for {len(upload_data)} dates")
            
            # Prüfe ob Daten für heute vorhanden sind
            uploads_today = upload_data.get(today, [])
            print(f"Uploads for today: {len(uploads_today)}")
            
            if uploads_today:
                print("Test data found - showing dialog...")
                show_test_dialog()
            else:
                print("No test data found")
                messagebox.showinfo("Test", "Keine Test-Uploads für heute vorhanden")
                
        except Exception as e:
            print(f"Error in calendar test: {e}")
            traceback.print_exc()
    
    print("🧪 Calendar Dialog Debug Test")
    print("=" * 40)
    
    # Create test app
    app = ctk.CTk()
    app.title("Calendar Dialog Test")
    app.geometry("600x400")
    
    # Main frame
    main_frame = ctk.CTkFrame(app)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    title_label = ctk.CTkLabel(
        main_frame,
        text="Calendar Dialog Debug Test",
        font=ctk.CTkFont(size=20, weight="bold")
    )
    title_label.pack(pady=20)
    
    # Test buttons
    test_btn1 = ctk.CTkButton(
        main_frame,
        text="Test Dialog direkt",
        command=show_test_dialog,
        height=40,
        width=200
    )
    test_btn1.pack(pady=10)
    
    test_btn2 = ctk.CTkButton(
        main_frame,
        text="Test Kalender-Funktionalität",
        command=test_calendar_functionality,
        height=40,
        width=200
    )
    test_btn2.pack(pady=10)
    
    # Info
    info_label = ctk.CTkLabel(
        main_frame,
        text="Klicken Sie auf die Buttons, um verschiedene Aspekte\ndes Kalender-Dialogs zu testen.",
        font=ctk.CTkFont(size=12),
        text_color="gray"
    )
    info_label.pack(pady=20)
    
    # Start the app
    app.mainloop()

if __name__ == "__main__":
    test_calendar_dialog()
