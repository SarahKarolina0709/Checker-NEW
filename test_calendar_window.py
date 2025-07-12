#!/usr/bin/env python3
"""
Test-Script für das separate Kalender-Fenster
"""

import sys
import os
import logging
from datetime import datetime, date
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

import customtkinter as ctk
from welcome_screen_components.customer_section_with_calendar import CustomerSectionWithCalendar
from ui_theme import UITheme

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestCalendarWindow:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Test: Kalender-Fenster")
        self.root.geometry("400x300")
        
        # Apply theme
        ctk.set_appearance_mode(UITheme.APPEARANCE_MODE)
        ctk.set_default_color_theme(UITheme.COLOR_THEME)
        
        self.create_test_ui()
        
    def create_test_ui(self):
        """Erstellt die Test-UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="📅 Kalender-Fenster Test",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=24, weight="bold")
        )
        title_label.pack(pady=(0, 30))
        
        # Create customer section (contains calendar)
        self.customer_section = CustomerSectionWithCalendar(main_frame)
        self.customer_section.pack(fill="both", expand=True)
        
        # Test button
        test_btn = ctk.CTkButton(
            main_frame,
            text="🔍 Kalender-Fenster öffnen",
            command=self.test_calendar_window,
            height=50,
            **UITheme.BUTTON_STYLE_PRIMARY
        )
        test_btn.pack(pady=(20, 0))
        
    def test_calendar_window(self):
        """Testet das Kalender-Fenster"""
        try:
            logger.info("Testing calendar window...")
            
            # Add some test upload data
            test_uploads = {
                date(2024, 1, 15): [
                    {
                        'customer': 'Test Kunde 1',
                        'file_name': 'test_dokument_1.pdf',
                        'upload_time': datetime(2024, 1, 15, 10, 30).strftime('%H:%M'),
                        'file_size': '2.5 MB'
                    },
                    {
                        'customer': 'Test Kunde 2',
                        'file_name': 'test_dokument_2.docx',
                        'upload_time': datetime(2024, 1, 15, 14, 45).strftime('%H:%M'),
                        'file_size': '1.8 MB'
                    }
                ],
                date(2024, 1, 20): [
                    {
                        'customer': 'Test Kunde 3',
                        'file_name': 'test_dokument_3.txt',
                        'upload_time': datetime(2024, 1, 20, 9, 15).strftime('%H:%M'),
                        'file_size': '0.5 MB'
                    }
                ],
                date.today(): [
                    {
                        'customer': 'Heute-Kunde',
                        'file_name': 'heute_dokument.pdf',
                        'upload_time': datetime.now().strftime('%H:%M'),
                        'file_size': '3.2 MB'
                    }
                ]
            }
            
            # Set test data
            self.customer_section.upload_data = test_uploads
            
            # Open calendar window
            self.customer_section.toggle_calendar()
            
            logger.info("Calendar window test completed successfully")
            
        except Exception as e:
            logger.error(f"Error testing calendar window: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Startet den Test"""
        logger.info("Starting calendar window test...")
        
        # Add instructions
        instructions = """
        KALENDER-FENSTER TEST
        
        1. Klicken Sie auf "Kalender-Fenster öffnen"
        2. Ein neues Fenster sollte sich öffnen
        3. Testen Sie die Navigation zwischen Monaten
        4. Klicken Sie auf Tage mit Uploads (hervorgehoben)
        5. Vergewissern Sie sich, dass Upload-Details angezeigt werden
        6. Testen Sie den Kunde-Filter
        7. Schließen Sie das Fenster mit dem "Schließen"-Button
        
        Erwartete Funktionen:
        - Separates, größenveränderbares Kalender-Fenster
        - Monatliche Navigation
        - Hervorhebung von Upload-Tagen
        - Detailansicht beim Klicken auf Upload-Tage
        - Kundenfilter
        - Statistiken
        """
        
        print(instructions)
        
        self.root.mainloop()

if __name__ == "__main__":
    test = TestCalendarWindow()
    test.run()
