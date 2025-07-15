#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der integrierten Upload-Funktionalität

Testet:
- Dateiauswahl
- Kundenauswahl
- Upload-Prozess
- Ordnererstellung
"""

import customtkinter as ctk
import sys
import os

# Pfad konfigurieren
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

from customer_management_utils import CustomerManager
from src.ui.customer_dialogs import CustomerSelectionDialog, UploadProcessDialog

def test_upload_integration():
    """Testet die Upload-Integration."""
    
    # CustomTkinter initialisieren
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Hauptfenster
    root = ctk.CTk()
    root.title("Test: Upload-Integration")
    root.geometry("400x300")
    
    # Customer Manager
    customer_manager = CustomerManager()
    
    def test_file_upload():
        """Testet den kompletten Upload-Workflow."""
        from tkinter import filedialog
        
        print("=== Upload-Test gestartet ===")
        
        # 1. Dateien auswählen (simuliert)
        files = filedialog.askopenfilenames(
            title="Test-Dateien auswählen",
            filetypes=[("Alle Dateien", "*.*")]
        )
        
        if not files:
            print("❌ Keine Dateien ausgewählt")
            return
            
        print(f"✅ {len(files)} Dateien ausgewählt:")
        for file in files:
            print(f"   📄 {os.path.basename(file)}")
        
        # 2. Kunde auswählen
        customer_dialog = CustomerSelectionDialog(root, customer_manager)
        selected_customer = customer_dialog.get_result()
        
        if not selected_customer:
            print("❌ Kein Kunde ausgewählt")
            return
            
        customer_name = selected_customer.get('name', 'Unbekannt')
        print(f"✅ Kunde ausgewählt: {customer_name}")
        
        # 3. Upload-Prozess
        upload_dialog = UploadProcessDialog(
            root, 
            files, 
            selected_customer, 
            customer_manager,
            None  # Upload Manager optional
        )
        result = upload_dialog.get_result()
        
        if result:
            print("✅ Upload erfolgreich abgeschlossen!")
            print(f"   📁 Ordner: {result.get('upload_folder', 'Unbekannt')}")
        else:
            print("❌ Upload abgebrochen")
    
    def show_customers():
        """Zeigt verfügbare Kunden an."""
        print("\n=== Verfügbare Kunden ===")
        if customer_manager.customers_data:
            for customer_id, data in customer_manager.customers_data.items():
                print(f"👤 {data.get('name', 'Unbekannt')} ({data.get('code', 'N/A')})")
        else:
            print("❌ Keine Kunden verfügbar")
        print()
    
    # UI erstellen
    header = ctk.CTkLabel(
        root,
        text="🧪 Upload-Integration Test",
        font=ctk.CTkFont(size=20, weight="bold")
    )
    header.pack(pady=20)
    
    # Buttons
    customers_btn = ctk.CTkButton(
        root,
        text="👥 Kunden anzeigen",
        command=show_customers,
        height=40
    )
    customers_btn.pack(pady=10, padx=20, fill="x")
    
    upload_btn = ctk.CTkButton(
        root,
        text="📤 Upload testen",
        command=test_file_upload,
        height=40,
        fg_color="#10B981",
        hover_color="#059669"
    )
    upload_btn.pack(pady=10, padx=20, fill="x")
    
    # Info
    info_label = ctk.CTkLabel(
        root,
        text=f"Aktuelle Kunden: {len(customer_manager.customers_data)}",
        font=ctk.CTkFont(size=12),
        text_color="gray"
    )
    info_label.pack(pady=10)
    
    # Initial Kunden anzeigen
    show_customers()
    
    root.mainloop()

if __name__ == "__main__":
    test_upload_integration()
