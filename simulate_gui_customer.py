#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simuliere GUI-Interaktion für Customer-Addition
"""

import sys
import os
import time

# Stelle sicher, dass das aktuelle Verzeichnis im Python-Pfad ist
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def simulate_customer_addition():
    """Simuliere die Customer-Addition in der GUI"""
    try:
        print("=== Simuliere GUI Customer-Addition ===")
        
        # Aktiviere Debug-Modus für bessere Ausgaben
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        # Importiere welcome_screen
        print("1. Importiere Welcome Screen...")
        import welcome_screen
        
        # Erstelle eine Mock-GUI-Instanz (ohne tatsächliche GUI)
        print("2. Erstelle Mock-GUI-Instanz...")
        
        class MockEntry:
            def __init__(self, value=""):
                self.value = value
                
            def get(self):
                return self.value
                
            def strip(self):
                return self.value.strip()
        
        class MockUI:
            def show_toast(self, message, type):
                print(f"TOAST: {message} ({type})")
        
        # Simuliere die Hauptfunktionen
        class MockWelcomeScreen:
            def __init__(self):
                # Initialisiere Manager
                from customer_manager import CustomerManager
                from src.managers.kunden_manager import KundenManager as CoreKundenManager
                
                self.customer_manager = CustomerManager(
                    customers_file="test_customers.json",
                    projects_base_path="projects"
                )
                
                self.kunden_manager = CoreKundenManager(base_dir="projects")
                self.ui_manager = MockUI()
                
                # Mock customer_entry
                self.customer_entry = MockEntry("Test GUI Kunde")
                
                print(f"   Customer Manager: {self.customer_manager}")
                print(f"   Kunden Manager: {self.kunden_manager}")
                print(f"   UI Manager: {self.ui_manager}")
                
            def _show_enhanced_toast(self, message, type):
                print(f"ENHANCED TOAST: {message} ({type})")
                
            def _handle_customer_added_successfully(self, customer_name):
                print(f"SUCCESS HANDLER: Kunde '{customer_name}' erfolgreich hinzugefügt!")
                
            def _show_duplicate_warning_dialog(self, customer_name, similar_customers):
                print(f"DUPLICATE WARNING: '{customer_name}' hat ähnliche Kunden: {similar_customers}")
                
            def _add_customer_legacy(self, customer_name):
                print(f"LEGACY FALLBACK: Füge '{customer_name}' über Legacy-Methode hinzu")
        
        # Erstelle Mock-Instanz
        mock_screen = MockWelcomeScreen()
        
        # Simuliere die _add_customer Methode (kopiere aus welcome_screen.py)
        print("3. Simuliere _add_customer Aufruf...")
        
        def simulate_add_customer():
            try:
                customer_name = mock_screen.customer_entry.get().strip()
                print(f"   Kunde Name aus Entry: '{customer_name}'")
                
                if not customer_name:
                    mock_screen.ui_manager.show_toast("Bitte geben Sie einen Kundennamen ein", "warning")
                    return
                
                # ✅ USE BUSINESS LOGIC MANAGER - Try both managers
                success = False
                message = ""
                similar_customers = []
                
                print("   Versuche customer_manager...")
                if mock_screen.customer_manager:
                    try:
                        success, message, similar_customers = mock_screen.customer_manager.add_customer(customer_name)
                        print(f"   customer_manager Ergebnis: success={success}, msg='{message}', similar={similar_customers}")
                    except Exception as e:
                        print(f"   Error with customer_manager: {e}")
                        success = False
                
                # If customer_manager failed or doesn't exist, try kunden_manager
                if not success and hasattr(mock_screen, 'kunden_manager') and mock_screen.kunden_manager:
                    print("   Versuche kunden_manager...")
                    try:
                        success, message, similar_customers = mock_screen.kunden_manager.add_customer(customer_name)
                        print(f"   kunden_manager Ergebnis: success={success}, msg='{message}', similar={similar_customers}")
                    except Exception as e:
                        print(f"   Error with kunden_manager: {e}")
                        success = False
                
                if success:
                    # Customer added successfully
                    print("   -> Kunde erfolgreich hinzugefügt!")
                    mock_screen._handle_customer_added_successfully(customer_name)
                elif similar_customers:
                    # Similar customers found - show dialog
                    print("   -> Ähnliche Kunden gefunden!")
                    mock_screen._show_duplicate_warning_dialog(customer_name, similar_customers)
                elif not success and (mock_screen.customer_manager or hasattr(mock_screen, 'kunden_manager')):
                    # Error occurred
                    print("   -> Fehler aufgetreten!")
                    mock_screen.ui_manager.show_toast(message, "error")
                else:
                    # Fallback to old method
                    print("   -> Fallback zur Legacy-Methode!")
                    mock_screen._add_customer_legacy(customer_name)
                    
            except Exception as e:
                error_msg = f"Fehler beim Hinzufügen des Kunden: {str(e)}"
                print(f"   -> Exception: {error_msg}")
                mock_screen.ui_manager.show_toast(error_msg, "error")
        
        # Führe die Simulation aus
        simulate_add_customer()
        
        print("\n=== Simulation abgeschlossen ===")
        
    except Exception as e:
        print(f"❌ Simulation Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simulate_customer_addition()
