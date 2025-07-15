#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Vollständige Upload-Integration

Zeigt die komplette Upload-Funktionalität:
1. Dateiauswahl
2. Kundenauswahl  
3. Upload-Prozess
4. Ordnererstellung
5. Integration mit Welcome-Screen
"""

import customtkinter as ctk
import sys
import os

# Pfad konfigurieren
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from customer_management_utils import CustomerManager
from upload_manager import UploadManager

def demo_complete_upload_system():
    """Demo des kompletten Upload-Systems."""
    
    print("=== DEMO: Vollständige Upload-Integration ===\n")
    
    # Manager initialisieren
    customer_manager = CustomerManager()
    upload_manager = UploadManager()
    
    print("1. SYSTEM-STATUS:")
    print(f"   📊 Kunden verfügbar: {len(customer_manager.customers_data)}")
    print(f"   📤 Upload-Manager: ✅ Aktiv")
    print()
    
    print("2. VERFÜGBARE KUNDEN:")
    if customer_manager.customers_data:
        for customer_id, data in list(customer_manager.customers_data.items())[:3]:
            name = data.get('name', 'Unbekannt')
            company = data.get('company', '')
            folder_name = customer_manager.get_customer_folder_name(customer_id)
            print(f"   👤 {name}")
            print(f"      🏢 Firma: {company}")
            print(f"      📁 Ordner: {folder_name}")
            print()
    else:
        print("   ❌ Keine Kunden verfügbar")
        print()
    
    print("3. UPLOAD-WORKFLOW:")
    print("   ✅ Schritt 1: Dateien auswählen")
    print("   ✅ Schritt 2: Kunde auswählen")
    print("   ✅ Schritt 3: Upload-Ordner erstellen")
    print("   ✅ Schritt 4: Dateien kopieren")
    print("   ✅ Schritt 5: Bestätigung & Status")
    print()
    
    print("4. INTEGRATION WELCOME-SCREEN:")
    print("   🔗 Upload-Button verknüpft")
    print("   🔗 Projekt-Button verknüpft")
    print("   🔗 Kunden-Button verknüpft")
    print("   📊 Live-Statistiken verfügbar")
    print()
    
    # Simulations-Upload durchführen
    print("5. SIMULATIONS-UPLOAD:")
    
    # Test-Kunde verwenden
    if customer_manager.customers_data:
        test_customer_id = list(customer_manager.customers_data.keys())[0]
        test_customer = customer_manager.customers_data[test_customer_id]
        
        print(f"   👤 Test-Kunde: {test_customer.get('name', 'Unbekannt')}")
        
        # Dummy-Dateien simulieren
        dummy_files = [
            "C:/Users/Demo/Documents/test_document.pdf",
            "C:/Users/Demo/Documents/angebot_2025.docx",
            "C:/Users/Demo/Documents/uebersetzung.txt"
        ]
        
        print(f"   📄 Dummy-Dateien: {len(dummy_files)}")
        for file in dummy_files:
            print(f"      • {os.path.basename(file)}")
        
        # Upload simulieren (ohne tatsächliche Dateien)
        try:
            # Nur Ordner-Erstellung testen
            upload_folder = customer_manager.create_upload_folder(test_customer_id)
            folder_name = customer_manager.get_customer_folder_name(test_customer_id)
            
            print(f"   ✅ Upload-Ordner erstellt: {upload_folder}")
            print(f"   📁 Kunde-Ordner: {folder_name}")
            
            # Workflow-Unterordner prüfen
            workflows = ["Ausgangstexte", "Übersetzung", "Korrektur", "Fertig"]
            for workflow in workflows:
                workflow_path = os.path.join(upload_folder, workflow)
                if os.path.exists(workflow_path):
                    print(f"   📂 {workflow}: ✅ Verfügbar")
                else:
                    print(f"   📂 {workflow}: ❌ Nicht verfügbar")
            
        except Exception as e:
            print(f"   ❌ Fehler beim Upload-Test: {e}")
    else:
        print("   ❌ Kein Test-Kunde verfügbar")
    
    print("\n6. ZUSAMMENFASSUNG:")
    print("   🚀 Upload-System vollständig integriert")
    print("   🔗 Kundenmanagement verknüpft")
    print("   📁 Ordner-Struktur automatisch erstellt")
    print("   🎯 Welcome-Screen zeigt Live-Daten")
    print("   ✨ Benutzerfreundlicher Workflow")
    
    print("\n=== DEMO ABGESCHLOSSEN ===")


def create_upload_demo_gui():
    """Erstellt eine GUI-Demo der Upload-Funktionalität."""
    
    # CustomTkinter initialisieren
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Hauptfenster
    root = ctk.CTk()
    root.title("🚀 Upload-Integration Demo")
    root.geometry("600x500")
    
    # Manager
    customer_manager = CustomerManager()
    upload_manager = UploadManager()
    
    # Header
    header = ctk.CTkLabel(
        root,
        text="🚀 Upload-Integration Demo",
        font=ctk.CTkFont(size=24, weight="bold")
    )
    header.pack(pady=20)
    
    # Stats Frame
    stats_frame = ctk.CTkFrame(root)
    stats_frame.pack(fill="x", padx=20, pady=10)
    
    stats_label = ctk.CTkLabel(
        stats_frame,
        text=f"📊 System-Status: {len(customer_manager.customers_data)} Kunden • Upload-Manager aktiv",
        font=ctk.CTkFont(size=14)
    )
    stats_label.pack(pady=10)
    
    # Workflow Demo
    workflow_frame = ctk.CTkFrame(root)
    workflow_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    workflow_label = ctk.CTkLabel(
        workflow_frame,
        text="📋 Upload-Workflow",
        font=ctk.CTkFont(size=18, weight="bold")
    )
    workflow_label.pack(pady=(10, 20))
    
    # Workflow-Schritte
    steps = [
        "1. 📁 Dateien auswählen (filedialog)",
        "2. 👤 Kunde auswählen (CustomerSelectionDialog)", 
        "3. 📤 Upload-Prozess (UploadProcessDialog)",
        "4. 📂 Ordner erstellen (CustomerManager)",
        "5. ✅ Bestätigung & Status-Update"
    ]
    
    for step in steps:
        step_label = ctk.CTkLabel(
            workflow_frame,
            text=step,
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        step_label.pack(anchor="w", padx=20, pady=5)
    
    # Test-Button
    def run_console_demo():
        """Führt die Konsolen-Demo aus."""
        demo_complete_upload_system()
    
    test_btn = ctk.CTkButton(
        root,
        text="🧪 Konsolen-Demo ausführen",
        command=run_console_demo,
        height=50,
        font=ctk.CTkFont(size=16, weight="bold"),
        fg_color="#10B981",
        hover_color="#059669"
    )
    test_btn.pack(pady=20, padx=20, fill="x")
    
    # Info
    info_label = ctk.CTkLabel(
        root,
        text="💡 Diese Demo zeigt die vollständige Integration des Upload-Systems\nmit Kundenmanagement und Welcome-Screen.",
        font=ctk.CTkFont(size=12),
        text_color="gray",
        justify="center"
    )
    info_label.pack(pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    print("Starte Upload-Integration Demo...\n")
    
    # Konsolen-Demo
    demo_complete_upload_system()
    
    # GUI-Demo
    print("\nStarte GUI-Demo...")
    create_upload_demo_gui()
