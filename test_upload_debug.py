#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Skript zur Überprüfung der Upload-Funktionalität und Ordnerstruktur
"""

import os
import shutil
from datetime import datetime

def clean_folder_name(name):
    """Bereinigt einen Namen für die Verwendung als Ordnername."""
    # Ungültige Zeichen für Windows-Ordnernamen entfernen
    invalid_chars = '<>:"/\\|?*'
    clean_name = ''.join(c for c in name if c not in invalid_chars)
    
    # Umlaute ersetzen
    umlaut_map = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss', 
                 'Ä': 'AE', 'Ö': 'OE', 'Ü': 'UE'}
    for umlaut, replacement in umlaut_map.items():
        clean_name = clean_name.replace(umlaut, replacement)
    
    # Mehrfache Leerzeichen entfernen und durch Unterstrich ersetzen
    clean_name = '_'.join(clean_name.split())
    
    # Maximale Länge begrenzen
    if len(clean_name) > 50:
        clean_name = clean_name[:50]
    
    return clean_name

def test_upload_workflow():
    """Testet die Upload-Workflow-Funktionalität."""
    print("🔍 Upload-Workflow Test gestartet...\n")
    
    # Test-Daten
    test_customer = {
        'id': 1,
        'name': 'Test GmbH & Co. KG',
        'code': 'TST',
        'email': 'info@test.de',
        'contact': 'Geschäftsführung'
    }
    
    # Basis-Pfad
    base_path = os.getcwd()  # Aktueller Ordner
    print(f"📁 Basis-Pfad: {base_path}")
    
    # Kundenordner erstellen
    customer_name_clean = clean_folder_name(test_customer['name'])
    customer_folder = os.path.join(base_path, "TEST_" + customer_name_clean)
    print(f"👤 Bereinigter Kundenname: {customer_name_clean}")
    print(f"📂 Kundenordner: {customer_folder}")
    
    # Datumsordner erstellen
    today = datetime.now()
    date_folder_name = today.strftime("%Y-%m-%d")
    date_folder = os.path.join(customer_folder, date_folder_name)
    print(f"📅 Datumsordner: {date_folder}")
    
    # Workflow-Ordnerstruktur
    workflow_folders = {
        "01_Ausgangstext": "Hochgeladene Ausgangsdateien",
        "02_Angebot": "Angebotsdokumente und Kostenvoranschläge", 
        "03_Prüfung": "Qualitätsprüfung und Korrektur",
        "04_Finalisierung": "Finale Dokumente und Auslieferung"
    }
    
    print(f"\n🏗️ Erstelle Ordnerstruktur...")
    
    # Alle Ordner erstellen
    ausgangstext_folder = os.path.join(date_folder, "01_Ausgangstext")
    
    for folder_name, description in workflow_folders.items():
        folder_path = os.path.join(date_folder, folder_name)
        try:
            os.makedirs(folder_path, exist_ok=True)
            print(f"✅ Ordner erstellt: {folder_path}")
            
            # Info-Datei in jeden Ordner
            info_file = os.path.join(folder_path, "_INFO.txt")
            if not os.path.exists(info_file):
                with open(info_file, 'w', encoding='utf-8') as f:
                    f.write(f"📁 {folder_name}\n")
                    f.write(f"📝 {description}\n")
                    f.write(f"👥 Kunde: {test_customer['name']}\n")
                    f.write(f"📅 Erstellt: {today.strftime('%Y-%m-%d %H:%M:%S')}\n")
                print(f"   📄 Info-Datei erstellt: _INFO.txt")
        except Exception as e:
            print(f"❌ Fehler beim Erstellen von {folder_path}: {e}")
    
    print(f"\n📁 Ausgangstext-Ordner: {ausgangstext_folder}")
    print(f"📁 Existiert: {os.path.exists(ausgangstext_folder)}")
    
    # Test-Datei erstellen und kopieren
    test_file = os.path.join(base_path, "test_upload_datei.txt")
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(f"Test-Datei für Upload-Test\n")
            f.write(f"Kunde: {test_customer['name']}\n")
            f.write(f"Datum: {today.strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"\n📄 Test-Datei erstellt: {test_file}")
        
        # Datei in Ausgangstext-Ordner kopieren
        if os.path.exists(ausgangstext_folder):
            destination = os.path.join(ausgangstext_folder, "test_upload_datei.txt")
            shutil.copy2(test_file, destination)
            print(f"📋 Datei kopiert nach: {destination}")
            print(f"📋 Kopie existiert: {os.path.exists(destination)}")
            
            # Dateiinhalt prüfen
            if os.path.exists(destination):
                with open(destination, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"📄 Dateiinhalt:\n{content}")
        else:
            print("❌ Ausgangstext-Ordner existiert nicht!")
            
    except Exception as e:
        print(f"❌ Fehler beim Dateien-Test: {e}")
    
    # Ordnerinhalt anzeigen
    print(f"\n📂 Ordnerstruktur-Übersicht:")
    if os.path.exists(customer_folder):
        for root, dirs, files in os.walk(customer_folder):
            level = root.replace(customer_folder, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}📁 {os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}📄 {file}")
    
    print(f"\n✅ Upload-Workflow Test abgeschlossen!")
    print(f"🧹 Test-Dateien können manuell gelöscht werden: {customer_folder}")

if __name__ == "__main__":
    test_upload_workflow()
