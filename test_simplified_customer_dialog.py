#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test des vereinfachten Customer Dialog
"""

import customtkinter as ctk
import sys
import os

# Pfad konfigurieren
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

from customer_management_utils import CustomerManager
from src.ui.customer_dialogs import AddCustomerDialog

def test_add_customer_dialog():
    """Testet den vereinfachten Add Customer Dialog."""
    
    # CustomTkinter initialisieren
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Hauptfenster
    root = ctk.CTk()
    root.title("Test: Vereinfachter Kunde hinzufügen Dialog")
    root.geometry("300x200")
    
    # Customer Manager
    customer_manager = CustomerManager()
    
    def show_dialog():
        """Zeigt den Dialog an."""
        dialog = AddCustomerDialog(root, customer_manager)
        result = dialog.get_result()
        
        if result:
            print(f"✅ Neuer Kunde erstellt:")
            print(f"   Name: {result.get('name')}")
            print(f"   Code: {result.get('code')}")
            print(f"   Company: {result.get('company')}")
            print(f"   Contact: {result.get('contact', 'Nicht ausgefüllt')}")
            print(f"   Email: {result.get('email', 'Nicht ausgefüllt')}")
        else:
            print("❌ Dialog wurde abgebrochen")
    
    # Test-Button
    test_btn = ctk.CTkButton(
        root,
        text="🧪 Neuen Kunden hinzufügen",
        command=show_dialog,
        height=50,
        font=ctk.CTkFont(size=16, weight="bold")
    )
    test_btn.pack(expand=True)
    
    # Aktueller Stand anzeigen
    info_label = ctk.CTkLabel(
        root,
        text=f"Aktuelle Kunden: {len(customer_manager.customers_data)}",
        font=ctk.CTkFont(size=12),
        text_color="gray"
    )
    info_label.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_add_customer_dialog()
